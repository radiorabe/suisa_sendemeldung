#!/usr/bin/env python3
"""
SUISA Sendemeldung bugs SUISA with email once per month.

Fetches data on our playout history and formats them in a CSV file format
containing the data (like Track, Title and ISRC) requested by SUISA. Also takes care of sending
the report to SUISA via email for hands-off operations.
"""
from csv import writer
from datetime import date, datetime, timedelta
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from io import StringIO
from os.path import basename, expanduser
from smtplib import SMTP
from string import Template

import cridlib
import pytz
from configargparse import ArgumentParser
from dateutil.relativedelta import relativedelta
from iso3901 import ISRC

from .acrclient import ACRClient

_EMAIL_TEMPLATE = """
Hallo SUISA

Im Anhang finden Sie die Sendemeldung von $station_name für den $month $year.

Wir senden ihnen diese Sendemeldung da wir bis Ende $previous_year nicht informiert
wurden, dass $station_name im laufenden Jahr von der Meldepflicht befreit ist.

In der Sendungsmeldung enthalten sind die unter Buchstaben G im Tarif
"Gemeinsamer Tarif S 2020 - 2023" genannten Programmangaben in elektronischer
Form. Es handelt sich bei der Datei um eine Comma-Separated Values (CSV)
Datei welche dem RFC 4180 Standard folgt.

Diese Sendemeldung enthält unter anderem folgende Angaben:

- Titel des Musikwerks
- Name des Komponisten
- Name des bzw. der Hauptinterpreten
- Label
- ISRC
- vom Sender der Aufnahme selbst zugewiesene Identifikationsnummer
- Sendezeit
- Sendedauer

Die Datei folgt nach bestem Wissen und Gewissen und wo dies technisch möglich
ist der Vorlage in "Gemeinsamer Tarif S 2020 - 2023" Anhang 1.

Das Feld ISRC ist dabei mindestens in Fällen wo der ISRC zusammen mit der Aufnahme
vom Lieferanten der Aufnahme in irgendeiner Form mitgeteilt bzw. mitgeliefert
wurde angegeben. Wir ergänzen diese Angaben wo möglich aus unseren eigenen
Datenbeständen und arbeiten zu diesem Zweck auch mit externen Partnern zusammen.
Nachmeldungen und Korrekturen von ISRC werden wir selbstverständlich sofort
verarbeiten und ihnen mitteilen.

Wir bitten sie höflich uns den Erhalt wie auch die erfolgreiche, automatisierte
Verarbeitung dieser Sendemeldung zu bestätigen. Bitte kontaktieren sie uns
dringlich und unverzüglich falls diese Sendemeldung Mängel wie Inkorrektheit
oder andere Missstände wie Fehler oder Lücken aufweist. Beanstandungen zu dieser
Sendemeldung lassen sie uns bitte in den nächsten drei Monaten vor dem $in_three_months
zukommen. Im Falle einer Beanstandung streben wir an etwaige Mängel raschmöglichst
innerhalb der Nachfrist von 45 Tagen zu beheben.

Diese Email wurde automatisch generiert. Bei vertraglichen Fragen erreichen
sie uns an besten zu Bürozeiten unter $responsible_phone. Technische Anliegen
im Zusammenhang mit der Sendemeldung melden sie bitte ebenda oder bevorzugt
direkt per Email an $responsible_email.

Freundliche Grüsse,
$station_name
"""


def validate_arguments(parser, args):
    """Validate the arguments provided to the script.

    After this function we are sure that there are no conflicts in the arguments.

    Arguments:
        parser: the ArgumentParser to use for throwing errors
        args: the arguments to validate
    """
    msgs = []
    # check length of access_key
    if not len(args.access_key) == 32:
        msgs.append(
            f"wrong format on access_key, expected 32 characters but got {len(args.access_key)}"
        )
    # check length of stream_id
    if not len(args.stream_id) == 9:
        msgs.append(
            f"wrong format on stream_id, expected 9 characters but got {len(args.stream_id)}"
        )
    # one output option has to be set
    if not (args.csv or args.email or args.stdout):
        msgs.append(
            "no output option has been set, specify one of --csv, --email or --stdout"
        )
    # last_month is in conflict with start_date and end_date
    if args.last_month and (args.start_date or args.end_date):
        msgs.append("argument --last_month not allowed with --start_date or --end_date")
    # exit if there are error messages
    if msgs:
        parser.error("\n- " + "\n- ".join(msgs))


def get_arguments(parser: ArgumentParser):  # pragma: no cover
    """Create :class:`ArgumentParser` with arguments.

    Arguments:
        parser: the parser to add arguments

    Returns:
        args: the parsed args from the parser
    """
    parser.add_argument(
        "--access_key",
        env_var="ACCESS_KEY",
        help="the access key for ACRCloud (required)",
        required=True,
    )
    parser.add_argument(
        "--stream_id",
        env_var="STREAM_ID",
        help="the id of the stream at ACRCloud (required)",
        required=True,
    )
    parser.add_argument(
        "--station-name",
        env_var="STATION_NAME",
        help="Station name, used in Output and Emails",
        default="Radio Bern RaBe",
    )
    parser.add_argument(
        "--station-name-short",
        env_var="STATION_NAME_SHORT",
        help="Shortname for station as used in Filenames (locally and in attachment)",
        default="rabe",
    )
    parser.add_argument(
        "--csv", env_var="CSV", help="create a csv file", action="store_true"
    )
    parser.add_argument(
        "--email", env_var="EMAIL", help="send an email", action="store_true"
    )
    parser.add_argument(
        "--email_from", env_var="EMAIL_FROM", help="the sender of the email"
    )
    parser.add_argument(
        "--email_to", env_var="EMAIL_TO", help="the recipients of the email"
    )
    parser.add_argument(
        "--email_cc", env_var="EMAIL_CC", help="the cc recipients of the email"
    )
    parser.add_argument(
        "--email_bcc", env_var="EMAIL_BCC", help="the bcc recipients of the email"
    )
    parser.add_argument(
        "--email_server",
        env_var="EMAIL_SERVER",
        help="the smtp server to send the mail with",
    )
    parser.add_argument(
        "--email_login",
        env_var="EMAIL_LOGIN",
        help="the username to logon to the smtp server (default: email_from)",
    )
    parser.add_argument(
        "--email_pass", env_var="EMAIL_PASS", help="the password for the smtp server"
    )
    parser.add_argument(
        "--email_subject",
        env_var="EMAIL_SUBJECT",
        help="the subject of the email",
        default="SUISA Sendemeldung",
    )
    parser.add_argument(
        "--email_text",
        env_var="EMAIL_TEXT",
        help="""
        A template for the Email text, placeholders are $station_name, $month, $year, $previous_year, $responsible_email, and $resonsible_phone.
        """,
        default=_EMAIL_TEMPLATE,
    )
    parser.add_argument(
        "--responsible-email",
        env_var="RESPONSIBLE_EMAIL",
        help="Used to hint whom to contact in the emails text.",
        required=True,
    )
    parser.add_argument(
        "--responsible-phone",
        env_var="RESPONSIBLE_PHONE",
        help="Used to hint whom to contact if you like phones in the emails text.",
        required=True,
    )
    parser.add_argument(
        "--start_date",
        env_var="START_DATE",
        help="the start date of the interval in format YYYY-MM-DD (default: 30 days\
                              before end_date)",
    )
    parser.add_argument(
        "--end_date",
        env_var="END_DATE",
        help="the end date of the interval in format YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--last_month",
        env_var="LAST_MONTH",
        action="store_true",
        help="download data of whole last month",
    )
    parser.add_argument(
        "--timezone",
        env_var="TIMEZONE",
        help="set the timezone for localization",
        default="UTC",
    )
    parser.add_argument(
        "--filename",
        env_var="FILENAME",
        help="""
        file to write to (default: <station_name_short>_<year>_<month>.csv when reporting last month, <station_name_short>_<start_date>.csv else)
        """,
    )
    parser.add_argument(
        "--stdout", env_var="STDOUT", help="also print to stdout", action="store_true"
    )
    args = parser.parse_args()
    validate_arguments(parser, args)
    return args


def parse_date(args):
    """Parse date from args.

    Arguments:
        args: the arguments provided to the script

    Returns:
        start_date: the start date of the requested interval
        end_date: the end date of the requested interval
    """
    # date parsing logic
    if args.last_month:
        today = date.today()
        # get first of this month
        this_month = today.replace(day=1)
        # last day of last month = first day of this month - 1 day
        end_date = this_month - timedelta(days=1)
        start_date = end_date.replace(day=1)
    else:
        if args.end_date:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        else:
            # if no end_date was set, default to today
            end_date = date.today()
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        else:
            # if no start_date was set, default to 30 days before end_date
            start_date = end_date - timedelta(days=30)
    return start_date, end_date


def parse_filename(args, start_date):
    """Parse filename from args and start_date.

    Arguments:
        args: the arguments provided to the script

    Returns:
        filename: the filename to use for the csv data
    """
    if args.filename:
        filename = args.filename
    # depending on date args either append the month or the start_date
    elif args.last_month:
        date_part = f"{start_date.strftime('%Y')}_{start_date.strftime('%m')}"
        filename = f"{args.station_name_short}_{date_part}.csv"
    else:
        filename = f"{args.station_name_short}_{start_date}.csv"
    return filename


def check_duplicate(entry_a, entry_b):
    """Check if two entries are duplicates by checking their acrid in all music items.

    Arguments:
        entry_a: first entry
        entry_b: second entry

    Returns:
        True if the entries are duplicates, False otherwise
    """
    try:
        entry_a = entry_a["metadata"]["music"]
    except KeyError:
        entry_a = entry_a["metadata"]["custom_files"]
    try:
        entry_b = entry_b["metadata"]["music"]
    except KeyError:
        entry_b = entry_b["metadata"]["custom_files"]
    for music_a in entry_a:
        for music_b in entry_b:
            if music_a["acrid"] == music_b["acrid"]:
                return True
    return False


def merge_duplicates(data):
    """Merge consecutive entries into one if they are duplicates.

    Arguments:
        data: The data provided by ACRClient

    Returns:
        data: The processed data
    """
    prev = data[0]
    mark = []
    for entry in data[1:]:
        if check_duplicate(prev, entry):
            prev["metadata"]["played_duration"] = (
                prev["metadata"]["played_duration"]
                + entry["metadata"]["played_duration"]
            )
            # mark entry for removal
            mark.append(entry)
        else:
            prev = entry
    # remove marked entries
    for entry in mark:
        data.remove(entry)
    return data


def funge_release_date(release_date):
    """Make a release_date from ACR conform to what seems to be the spec."""

    if release_date != "" and len(release_date) == 10:
        # we can make it look like what suisa has in their examples if it's the right length
        release_date = datetime.strptime(release_date, "%Y-%m-%d").strftime("%Y%m%d")
    elif len(release_date) != 4:
        # we discard other records since there is no way to convert records like a plain
        # year into dd/mm/yyyy properly without further guidance from whomever ingests
        # the data, unless they are exactly 4 chars and we blindly assume the record to
        # be just a plain year :shrug:
        release_date = ""
    return release_date


def get_artist(music):
    """Get artist from a given dict.

    Arguments:
        music: music dict from API

    Returns:
        artist: string representing the artist
    """
    artist = ""
    if music.get("artists") is not None:
        artists = music.get("artists")
        if isinstance(artists, list):
            artist = ", ".join([a.get("name") for a in artists])
        else:
            # Yet another 'wrong' entry in the database:
            # artists in custom_files was sometimes recorded as single value
            # @TODO also remove once way in the past? (2023-01-31)
            artist = artists
    elif music.get("artist") is not None:
        artist = music.get("artist")
    elif music.get("Artist") is not None:  # pragma: no cover
        # Uppercase is a hack needed for Jun 2021 since there is a 'wrong' entry
        # in the database. Going forward the record will be available as 'artist'
        # in lowercase.
        # @TODO remove once is waaaay in the past
        artist = music.get("Artist")
    return artist


def get_isrc(music):
    """Get a valid ISRC from the music record or return an empty string."""
    isrc = ""
    if music.get("external_ids", {}).get("isrc"):
        isrc = music.get("external_ids").get("isrc")
    elif music.get("isrc"):
        isrc = music.get("isrc")
    # was a list with a singular entry for a while back in 2021
    if isinstance(isrc, list):
        isrc = isrc[0]
    # some records contain the "ISRC" prefix that is described as legacy
    # in the ISRC handbook from IFPI.
    if isrc and isrc[:4] == "ISRC":
        isrc = isrc[4:]
    # take care of cases where the isrc is space delimited even though the
    # record is technically wrong but happens often enough to warrant this
    # hack.
    if isrc:
        isrc = isrc.replace(" ", "")

    if not ISRC.validate(isrc):
        isrc = ""
    return isrc


# all local vars are required, eight are already used for the csv entries
# pylint: disable-msg=too-many-locals
def get_csv(data, station_name=""):
    """Create SUISA compatible csv data.

    Arguments:
        data: To data to create csv from

    Returns:
        csv: The converted data
    """
    header = [
        "Titel",
        "Komponist",
        "Interpret",
        "Interpreten-Info",
        "Sender",
        "Sendedatum",
        "Sendedauer",
        "Sendezeit",
        "Werkverzeichnisangaben",
        "ISRC",
        "Label",
        "CD ID / Katalog-Nummer",
        "Aufnahmedatum",
        "Aufnahmeland",
        "Erstveröffentlichungsdatum",
        "Titel des Tonträgers (Albumtitel)",
        "Autor Text",
        "Track Nummer",
        "Genre",
        "Programm",
        "Bestellnummer",
        "Marke",
        "Label Code",
        "EAN/GTIN",
        "Identifikationsnummer",
    ]
    csv = StringIO()
    csv_writer = writer(csv, dialect="excel")
    csv_writer.writerow(header)

    for entry in data:
        metadata = entry.get("metadata")
        # parse timestamp
        timestamp = datetime.strptime(metadata.get("timestamp_local"), ACRClient.TS_FMT)

        ts_date = timestamp.strftime("%Y%m%d")
        ts_time = timestamp.strftime("%H:%M:%S")
        duration = timedelta(seconds=metadata.get("played_duration"))

        try:
            music = metadata.get("music")[0]
        except TypeError:
            music = metadata.get("custom_files")[0]
        title = music.get("title")

        artist = get_artist(music)

        composer = ", ".join(music.get("contributors", {}).get("composers", ""))

        isrc = get_isrc(music)
        label = music.get("label")

        # load some "best-effort" fields
        album = music.get("album", {}).get("name", "")
        upc = music.get("external_ids", {}).get("upc", "")
        release_date = funge_release_date(music.get("release_date", ""))

        # cridlib only supports timezone-aware datetime values, so we convert one
        timestamp_utc = pytz.utc.localize(
            datetime.strptime(metadata.get("timestamp_utc"), ACRClient.TS_FMT)
        )
        # we include the acrid in our CRID so we know about the data's provenience
        # in case any questions about the data we delivered are asked
        acrid = music.get("acrid")
        local_id = cridlib.get(timestamp=timestamp_utc, fragment=f"acrid={acrid}")

        csv_writer.writerow(
            [
                title,
                composer,
                artist,
                "",  # Interpreten-Info
                station_name,
                ts_date,
                duration,
                ts_time,
                "",  # Werkverzeichnisangaben
                isrc,
                label,
                "",  # CD ID / Katalog-Nummer
                "",  # Aufnahmedatum
                "",  # Aufnahmeland
                release_date,
                album,
                "",  # Autor Text
                "",  # Track Nummer
                "",  # Genre
                "",  # Programm
                "",  # Bestellnummer
                "",  # Marke
                "",  # Label Code
                upc,
                local_id,
            ]
        )
    return csv.getvalue()


def write_csv(filename, csv):  # pragma: no cover
    """Write contents of `csv` to file.

    Arguments:
        filename: The file to write to.
        csv: The data to write to `filename`.
    """
    with open(filename, mode="w", encoding="utf-8") as csvfile:
        csvfile.write(csv)


# reducing the arguments even more does not seem practical
# pylint: disable-msg=too-many-arguments,invalid-name
def create_message(sender, recipient, subject, text, filename, csv, cc=None, bcc=None):
    """Create email message.

    Arguments:
        sender: The sender of the email. Login will be made with this user.
        recipient: The recipient of the email. Can be a list.
        subject: The subject of the email.
        text: The body of the email.
        filename: The filename to attach `csv` by.
        csv: The attachment data.
    """
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    if cc:
        msg["Cc"] = cc
    if bcc:
        msg["Bcc"] = bcc
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject
    # set body
    msg.attach(MIMEText(text))
    # attach csv
    part = MIMEBase("text", "csv")
    part.set_payload(csv.encode("utf-8"))
    encode_base64(part)
    part.add_header(
        "Content-Disposition", f'attachment; filename="{basename(filename)}'
    )
    msg.attach(part)

    return msg


def send_message(msg, server="127.0.0.1", login=None, password=None):
    """Send email.

    Arguments:
        msg: The message to send (an email.messag.Message object)
        server: The SMTP server to use to send the email.
        password: The password for `sender`@`server`.
    """
    with SMTP(server) as smtp:
        smtp.starttls()
        if password:
            if login:
                smtp.login(login, password)
            else:
                smtp.login(msg["From"], password)
        smtp.send_message(msg)


def main():  # pragma: no cover
    """Entrypoint for SUISA Sendemeldung ."""
    default_config_file = basename(__file__).replace(".py", ".conf")
    # config file in /etc gets overriden by the one in $HOME which gets overriden by the one in the
    # current directory
    default_config_files = [
        "/etc/" + default_config_file,
        expanduser("~") + "/" + default_config_file,
        default_config_file,
    ]
    parser = ArgumentParser(
        default_config_files=default_config_files,
        description="ACRCloud client for SUISA reporting @ RaBe.",
    )
    args = get_arguments(parser)

    start_date, end_date = parse_date(args)
    filename = parse_filename(args, start_date)

    client = ACRClient(args.access_key)
    data = client.get_interval_data(
        args.stream_id, start_date, end_date, timezone=args.timezone
    )
    csv = get_csv(merge_duplicates(data), station_name=args.station_name)
    if args.email:
        email_subject = start_date.strftime(args.email_subject)
        # generate body
        text = Template(args.email_text).substitute(
            {
                "station_name": args.station_name,
                "month": start_date.strftime("%B"),
                "year": start_date.strftime("%Y"),
                "previous_year": (start_date - timedelta(days=365)).strftime("%Y"),
                "in_three_months": (end_date + relativedelta(months=+3)).strftime(
                    "%d. %B %Y"
                ),
                "responsible_email": args.responsible_email,
                "responsible_phone": args.responsible_phone,
            }
        )
        msg = create_message(
            args.email_from,
            args.email_to,
            email_subject,
            text,
            filename,
            csv,
            cc=args.email_cc,
            bcc=args.email_bcc,
        )
        send_message(
            msg,
            server=args.email_server,
            login=args.email_login,
            password=args.email_pass,
        )
    if args.csv:
        write_csv(filename, csv)
    if args.stdout:
        print(csv)


if __name__ == "__main__":  # pragma: no cover
    main()
