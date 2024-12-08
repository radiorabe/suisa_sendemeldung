"""SUISA Sendemeldung bugs SUISA with email once per month.

Fetches data on our playout history and formats them in a CSV file format
containing the data (like Track, Title and ISRC) requested by SUISA. Also
takes care of sending the report to SUISA via email for hands-off operations.
"""

from __future__ import annotations

import sys
from csv import reader, writer
from datetime import date, datetime, timedelta
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from io import BytesIO, StringIO
from pathlib import Path
from smtplib import SMTP
from string import Template
from typing import TYPE_CHECKING, Any

import cridlib
import pytz
from babel.dates import format_date
from configargparse import ArgumentParser  # type: ignore[import-untyped]
from dateutil.relativedelta import relativedelta
from iso3901 import ISRC
from openpyxl import Workbook
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.styles import Border, Font, PatternFill, Side
from tqdm import tqdm

from .acrclient import ACRClient

if TYPE_CHECKING:  # pragma: no cover
    from argparse import Namespace as ArgparseNamespace

    from openpyxl.worksheet.worksheet import Worksheet

_EMAIL_TEMPLATE = """
Hallo SUISA

Im Anhang finden Sie die Sendemeldung von $station_name für den $month $year.

Diese Sendemeldung erfolgt gemäss den Bestimmungen "Gemeinsamer Tarif S 2020 - 2024" [1] unter
Einhaltung der Einreichefrist für den Monat $month gemäss Ziffer 45 des Tarifs.

In der Sendungsmeldung enthalten sind die unter Buchstaben G (Verzeichnisse) des Tarifs
genannten Programmangaben, in elektronischer Form. Die Angaben richten sich nach dem
standardisierten Format gemäss der "Vorlage für Sendemeldungen: Gemeinsamer Tarif S" [2]
sowie der Abstimmung zwischen SUISA und $station_name.


Diese Sendemeldung enthält unter anderem die unter Ziffer 34 geforderten Angaben:

- Titel des Musikwerks
- Name des Komponisten
- Name des bzw. der Hauptinterpreten
- Label
- ISRC der benützten Aufnahme (sofern zusammen mit der Aufnahme vom Lieferanten der Aufnahme mitgeliefert)
- vom Sender der Aufnahme selbst zugewiesene Identifikationsnummer
- Sendezeit
- Sendedauer


Allfällige Beanstandungen oder technische Rückfragen zu dieser Sendemeldung müssen in
schriftlicher, elektronischer Form an $responsible_email gerichtet werden.

Beanstandungen müssen, gemäss Ziffer 46, bis spätestens in drei Monaten vor dem $in_three_months
erfolgen. Anschliessend gilt die Sendemeldung für $month $year als akzeptiert und die
Tarifbestimmungen als eingehalten.

Korrekt und termingerecht gemeldete Beanstandungen werden unter Berücksichtigung der
Nachfrist von 45 Tagen, gemäss Ziffer 46, bearbeitet.

Diese Email und Sendemeldung wurde automatisch generiert.

Freundliche Grüsse,
$station_name

[1] <https://www.suisa.ch/dam/jcr:1d82128b-8cc7-4cf0-b0ef-1890ae9d434d/GTS_2020-2024_GER.pdf>
[2] <https://www.suisa.ch/dam/jcr:6934be98-4319-4565-8936-05007d83fd35/Vorlage_fuer_Sendemeldungen__GTS__2020-2022.xlsx>

--
$email_footer
"""  # noqa: E501

_ACRTOKEN_MAXLEN = 32


def validate_arguments(parser: ArgumentParser, args: ArgparseNamespace) -> None:
    """Validate the arguments provided to the script.

    After this function we are sure that there are no conflicts in the arguments.

    Arguments:
    ---------
        parser: the ArgumentParser to use for throwing errors
        args: the arguments to validate

    """
    msgs = []
    # check length of bearer_token
    if not len(args.bearer_token) >= _ACRTOKEN_MAXLEN:
        msgs.append(
            "".join(
                (
                    "wrong format on bearer_token, "
                    "expected larger than 32 characters "
                    f"but got {len(args.bearer_token)}"
                ),
            ),
        )
    # check length of stream_id
    if len(args.stream_id) not in [9, 10]:
        msgs.append(
            (
                "wrong format on stream_id, "
                f"expected 9 or 10 characters but got {len(args.stream_id)}"
            ),
        )
    # crid mode can be local or cridlib
    if args.crid_mode not in ["cridlib", "local"]:
        msgs.append("wrong CRID mode, expected 'cridlib' or 'local'")
    # one output option has to be set
    if not (args.file or args.email or args.stdout):
        msgs.append(
            "no output option has been set, specify one of --file, --email or --stdout",
        )
    # xlsx cannot be printed to stdout
    if args.stdout and args.filetype == "xlsx":
        msgs.append("xlsx cannot be printed to stdout, please set --filetype to csv")
    # last_month is in conflict with start_date and end_date
    if args.last_month and (args.start_date or args.end_date):
        msgs.append("argument --last_month not allowed with --start_date or --end_date")
    # exit if there are error messages
    if msgs:
        parser.error("\n- " + "\n- ".join(msgs))


def get_arguments(parser: ArgumentParser, sysargs: list[str]) -> ArgparseNamespace:
    """Create :class:`ArgumentParser` with arguments.

    Arguments:
    ---------
        parser: the parser to add arguments
        sysargs: sys.arg[1:] or something else for testing

    Returns:
    -------
        args: the parsed args from the parser

    """
    parser.add_argument(
        "--bearer-token",
        env_var="BEARER_TOKEN",
        help="the bearer token for ACRCloud (required)",
        required=True,
    )
    parser.add_argument(
        "--project-id",
        env_var="PROJECT_ID",
        help="the id of the project at ACRCloud (required)",
        required=True,
    )
    parser.add_argument(
        "--stream-id",
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
        "--file",
        env_var="FILE",
        help="create file",
        action="store_true",
    )
    parser.add_argument(
        "--filetype",
        env_var="FILETYPE",
        help="filetype to attach to email or write to file",
        choices=("xlsx", "csv"),
        default="xlsx",
    )
    parser.add_argument(
        "--email",
        env_var="EMAIL",
        help="send an email",
        action="store_true",
    )
    parser.add_argument(
        "--email-from",
        env_var="EMAIL_FROM",
        help="the sender of the email",
    )
    parser.add_argument(
        "--email-to",
        env_var="EMAIL_TO",
        help="the recipients of the email",
    )
    parser.add_argument(
        "--email-cc",
        env_var="EMAIL_CC",
        help="the cc recipients of the email",
    )
    parser.add_argument(
        "--email-bcc",
        env_var="EMAIL_BCC",
        help="the bcc recipients of the email",
    )
    parser.add_argument(
        "--email-server",
        env_var="EMAIL_SERVER",
        help="the smtp server to send the mail with",
    )
    parser.add_argument(
        "--email-login",
        env_var="EMAIL_LOGIN",
        help="the username to logon to the smtp server (default: email_from)",
    )
    parser.add_argument(
        "--email-pass",
        env_var="EMAIL_PASS",
        help="the password for the smtp server",
    )
    parser.add_argument(
        "--email-subject",
        env_var="EMAIL_SUBJECT",
        help="""
        Template for subject of the email.

        Placeholders are $station_name, $year and $month.
        """,
        default="SUISA Sendemeldung von $station_name für $year-$month",
    )
    parser.add_argument(
        "--email-text",
        env_var="EMAIL_TEXT",
        help="""
        Template for email text.

        Placeholders are $station_name, $month, $year, $previous_year,
        $responsible_email, and $email_footer.
        """,
        default=_EMAIL_TEMPLATE,
    )
    parser.add_argument(
        "--email-footer",
        env_var="EMAIL_FOOTER",
        help="Footer for the Email",
        default="Email generated by <https://github.com/radiorabe/suisa_sendemeldung>",
    )
    parser.add_argument(
        "--responsible-email",
        env_var="RESPONSIBLE_EMAIL",
        help="Used to hint whom to contact in the emails text.",
    )
    parser.add_argument(
        "--start-date",
        env_var="START_DATE",
        help="the start date of the interval in format YYYY-MM-DD (default: 30 days\
                              before end_date)",
    )
    parser.add_argument(
        "--end-date",
        env_var="END_DATE",
        help="the end date of the interval in format YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--last-month",
        env_var="LAST_MONTH",
        action="store_true",
        help="download data of whole last month",
    )
    parser.add_argument(
        "--timezone",
        env_var="TIMEZONE",
        help="set the timezone for localization",
        required=True,
        default="UTC",
    )
    parser.add_argument(
        "--locale",
        env_var="LOCALE",
        help="set locale for date and time formatting",
        default="de_CH",
    )
    parser.add_argument(
        "--filename",
        env_var="FILENAME",
        help="""
        Output filename.

        Default:
        - <station_name_short>_<year>_<month>.csv when reporting last month
        - <station_name_short>_<start_date>.csv else
        """,
    )
    parser.add_argument(
        "--stdout",
        env_var="STDOUT",
        help="also print to stdout",
        action="store_true",
    )
    parser.add_argument(
        "--crid-mode",
        env_var="CRID_MODE",
        help="Choose how to generate CRID identifiers (cridlib or local)",
        default="cridlib",
    )
    args = parser.parse_args(sysargs)
    validate_arguments(parser, args)  # pragma: no cover
    return args  # pragma: no cover


def parse_date(args: ArgparseNamespace) -> tuple[date, date]:
    """Parse date from args.

    Arguments:
    ---------
        args: the arguments provided to the script

    Returns:
    -------
        start_date: the start date of the requested interval
        end_date: the end date of the requested interval

    """
    # date parsing logic
    if args.last_month:
        today = date.today()  # noqa: DTZ011
        # get first of this month
        this_month = today.replace(day=1)
        # last day of last month = first day of this month - 1 day
        end_date = this_month - timedelta(days=1)
        start_date = end_date.replace(day=1)
    else:
        if args.end_date:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()  # noqa: DTZ007
        else:
            # if no end_date was set, default to today
            end_date = date.today()  # noqa: DTZ011
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()  # noqa: DTZ007
        else:
            # if no start_date was set, default to 30 days before end_date
            start_date = end_date - timedelta(days=30)
    return start_date, end_date


def parse_filename(args: ArgparseNamespace, start_date: date) -> str:
    """Parse filename from args and start_date.

    Arguments:
    ---------
        args: the arguments provided to the script
        start_date: start of reporting period

    Returns:
    -------
        filename: the filename to use for the csv data

    """
    if args.filename:
        filename = args.filename
    # depending on date args either append the month or the start_date
    elif args.last_month:
        date_part = f"{start_date.strftime('%Y')}_{start_date.strftime('%m')}"
        filename = f"{args.station_name_short}_{date_part}.{args.filetype}"
    else:
        filename = (
            f"{args.station_name_short}_"
            f"{start_date.strftime('%Y-%m-%d')}.{args.filetype}"
        )
    return filename


def check_duplicate(entry_a: Any, entry_b: Any) -> bool:  # noqa: ANN401
    """Check if two entries are duplicates by checking their acrid in all music items.

    Arguments:
    ---------
        entry_a: first entry
        entry_b: second entry

    Returns:
    -------
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


def merge_duplicates(data: Any) -> Any:  # noqa: ANN401
    """Merge consecutive entries into one if they are duplicates.

    Arguments:
    ---------
        data: The data provided by ACRClient

    Returns:
    -------
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


def funge_release_date(release_date: str = "") -> str:
    """Make a release_date from ACR conform to what seems to be the spec."""
    if len(release_date) == 10:  # noqa: PLR2004
        # we can make it look like what suisa has in their examples if it's the
        # right length
        try:
            return datetime.strptime(release_date, "%Y-%m-%d").strftime("%Y%m%d")  # noqa: DTZ007
        except ValueError:
            return ""
    # we discard other records since there is no way to convert records like a plain
    # year into dd/mm/yyyy properly without further guidance from whomever ingests
    # the data, in some cases this means we discard data that only contain a year
    # since they dont have that amount of precision.
    return ""


def get_artist(music: Any) -> str:  # noqa: ANN401
    """Get artist from a given dict.

    Arguments:
    ---------
        music: music dict from API

    Returns:
    -------
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


def get_isrc(music: Any) -> str:  # noqa: ANN401
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


def get_csv(data: dict, args: ArgparseNamespace) -> str:
    """Create SUISA compatible csv data.

    Arguments:
    ---------
        data: To data to create csv from
        args: Parsed arguments

    Returns:
    -------
        csv: The converted data

    """
    station_name = args.station_name
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

    for entry in tqdm(data, desc="preparing tracks for report"):
        metadata = entry.get("metadata")
        # parse timestamp
        timestamp = datetime.strptime(metadata.get("timestamp_local"), ACRClient.TS_FMT)  # noqa: DTZ007

        ts_date = timestamp.strftime("%Y%m%d")
        ts_time = timestamp.strftime("%H:%M:%S")
        hours, remainder = divmod(metadata.get("played_duration"), 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        # required format of duration field: hh:mm:ss
        duration = f"{hours:02}:{minutes:02}:{seconds:02}"

        try:
            music = metadata.get("music")[0]
        except TypeError:
            music = metadata.get("custom_files")[0]
        title = music.get("title")

        artist = get_artist(music)

        composer = ", ".join(music.get("contributors", {}).get("composers", ""))
        works_composer = ", ".join(
            [
                c["name"]
                for c in [
                    item
                    for sublist in [w["creators"] for w in music.get("works", [])]
                    for item in sublist
                ]
                if c.get("role", "") in ["C", "Composer", "W", "Writer"]
            ],
        )
        if works_composer and (not composer or composer == artist):
            composer = works_composer

        isrc = get_isrc(music)
        label = music.get("label")

        # load some "best-effort" fields
        album = music.get("album", "")
        # it's a dict if it's from the ACRCloud bucket, a string if from a custom bucket
        if isinstance(album, dict):
            album = album.get("name", "")
        upc = music.get("external_ids", {}).get("upc", "")
        release_date = funge_release_date(music.get("release_date", ""))

        local_id: str
        # cridlib only supports timezone-aware datetime values, so we convert one
        timestamp_utc = pytz.utc.localize(
            datetime.strptime(metadata.get("timestamp_utc"), ACRClient.TS_FMT),  # noqa: DTZ007
        )
        # we include the acrid in our CRID so we know about the data's provenience
        # in case any questions about the data we delivered are asked
        acrid = music.get("acrid")

        if args.crid_mode == "cridlib":
            local_id = str(
                cridlib.get(timestamp=timestamp_utc, fragment=f"acrid={acrid}")
            )
        elif args.crid_mode == "local":
            local_id = f"{timestamp_utc.isoformat()}#acrid={acrid}"

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
            ],
        )
    return csv.getvalue()


def get_xlsx(data: Any, args: ArgparseNamespace) -> BytesIO:  # noqa: ANN401
    """Create SUISA compatible xlsx data.

    Arguments:
    ---------
        data: The data to create xlsx from
        args: Parsed arguments

    Returns:
    -------
        xlsx: The converted data as BytesIO object

    """
    csv = get_csv(data, args=args)
    csv_reader = reader(StringIO(csv))

    xlsx = BytesIO()
    workbook: Workbook = Workbook()
    if not workbook.active:  # pragma: no cover
        raise RuntimeError
    worksheet: Worksheet = workbook.active  # type: ignore[assignment]

    for row in csv_reader:
        worksheet.append(row)

    # the columns that should be styled as required (grey background)
    required_columns = [
        "Titel",
        "Komponist",
        "Interpret",
        "Sendedatum",
        "Sendedauer",
        "Sendezeit",
        "ISRC",
        "Label",
        "Label Code",
        "Identifikationsnummer",
    ]
    font = Font(name="Calibri", bold=True, size=12)
    side = Side(border_style="thick", color="000000")
    border = Border(top=side, left=side, right=side, bottom=side)
    fill = PatternFill("solid", bgColor="d9d9d9", fgColor="d9d9d9")
    for cell in worksheet[1]:  # xlsx is 1-indexed
        cell.font = font
        cell.border = border
        if cell.value in required_columns:
            cell.fill = fill

    # Try to approximate the required width by finding the longest values per column
    dims: dict[str, int] = {}
    calc_row: tuple[Cell | MergedCell, ...]
    for calc_row in worksheet.rows:
        for cell in calc_row:
            if isinstance(cell, Cell) and cell.value:
                dims[cell.column_letter] = max(
                    (dims.get(cell.column_letter, 0), len(str(cell.value))),
                )
    # apply estimated width to each column
    padding = 3
    for col, value in dims.items():
        worksheet.column_dimensions[col].width = value + padding

    workbook.save(xlsx)
    return xlsx


def write_csv(filename: str, csv: str) -> None:  # pragma: no cover
    """Write contents of `csv` to file.

    Arguments:
    ---------
        filename: The file to write to.
        csv: The data to write to `filename`.

    """
    with Path(filename).open("w", encoding="utf-8") as csvfile:
        csvfile.write(csv)


def write_xlsx(filename: str, xlsx: BytesIO) -> None:  # pragma: no cover
    """Write contents of `xlsx` to file.

    Arguments:
    ---------
        filename: The file to write to.
        xlsx: The data to write to `filename`.

    """
    with Path(filename).open("wb") as xlsxfile:
        xlsxfile.write(xlsx.getvalue())


def get_email_attachment(filename: str, filetype: str, data: Any) -> MIMEBase:  # noqa: ANN401
    """Create attachment based on required filetype and data.

    Arguments:
    ---------
        filename: The filename of the attachment
        filetype: The filetype of the attachment
        data: The attachment data

    """
    maintype: str
    subtype: str
    payload: str
    if filetype == "xlsx":
        maintype = "application"
        subtype = "vnd.ms-excel"
        payload = data.getvalue()
    elif filetype == "csv":
        maintype = "text"
        subtype = "csv"
        payload = data.encode("utf-8")
        part = MIMEBase("text", "csv")

    part = MIMEBase(maintype, subtype)
    part.set_payload(payload)
    encode_base64(part)
    part.add_header(
        "Content-Disposition", f"attachment; filename={Path(filename).name}"
    )
    return part


def create_message(  # noqa: PLR0913
    sender: str,
    recipient: str,
    subject: str,
    text: str,
    filename: str,
    filetype: str,
    data: Any,  # noqa: ANN401
    cc: str | None = None,
    bcc: str | None = None,
) -> MIMEMultipart:
    """Create email message.

    Arguments:
    ---------
        sender: The sender of the email. Login will be made with this user.
        recipient: The recipient of the email. Can be a list.
        subject: The subject of the email.
        text: The body of the email.
        filename: The filename of the attachment
        filetype: The filetype of the attachment
        data: The attachment data.
        cc: cc recipient
        bcc: bcc recipient

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
    msg.attach(get_email_attachment(filename, filetype, data))

    return msg


def send_message(
    msg: MIMEMultipart,
    server: str = "127.0.0.1",
    login: str | None = None,
    password: str | None = None,
) -> None:
    """Send email.

    Arguments:
    ---------
        msg: The message to send (an email.messag.Message object)
        server: The SMTP server to use to send the email.
        login: The username for `sender`@`server`.
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


def main() -> None:  # pragma: no cover
    """Entrypoint for SUISA Sendemeldung ."""
    default_config_file: str = Path(__file__).name.replace(".py", ".conf")
    # config file in /etc gets overriden by the one in $HOME which gets overriden by the
    # one in the current directory
    default_config_files = [
        str(Path("/etc") / default_config_file),
        str(Path("~").expanduser() / default_config_file),
        default_config_file,
    ]
    parser = ArgumentParser(
        default_config_files=default_config_files,
        description="ACRCloud client for SUISA reporting @ RaBe.",
    )
    args = get_arguments(parser, sys.argv[1:])

    start_date, end_date = parse_date(args)
    filename = parse_filename(args, start_date)

    client = ACRClient(bearer_token=args.bearer_token)
    data = client.get_interval_data(
        args.project_id,
        args.stream_id,
        start_date,
        end_date,
        timezone=args.timezone,
    )
    data = merge_duplicates(data)
    if args.filetype == "xlsx":
        data = get_xlsx(data, args=args)
    elif args.filetype == "csv":
        data = get_csv(data, args=args)
    if args.email:
        email_subject = Template(args.email_subject).substitute(
            {
                "station_name": args.station_name,
                "year": format_date(start_date, format="yyyy", locale=args.locale),
                "month": format_date(start_date, format="MM", locale=args.locale),
            },
        )
        # generate body
        text = Template(args.email_text).substitute(
            {
                "station_name": args.station_name,
                "month": format_date(start_date, format="MMMM", locale=args.locale),
                "year": format_date(start_date, format="yyyy", locale=args.locale),
                "previous_year": format_date(
                    start_date - timedelta(days=365),
                    format="yyyy",
                    locale=args.locale,
                ),
                "in_three_months": format_date(
                    datetime.now() + relativedelta(months=+3),  # noqa: DTZ005
                    format="long",
                    locale=args.locale,
                ),
                "responsible_email": args.responsible_email,
                "email_footer": args.email_footer,
            },
        )
        msg = create_message(
            args.email_from,
            args.email_to,
            email_subject,
            text,
            filename,
            args.filetype,
            data,
            cc=args.email_cc,
            bcc=args.email_bcc,
        )
        send_message(
            msg,
            server=args.email_server,
            login=args.email_login,
            password=args.email_pass,
        )
    if args.file and args.filetype == "xlsx":
        write_xlsx(filename, data)
    elif args.file and args.filetype == "csv":
        write_csv(filename, data)
    if args.stdout and args.filetype == "csv":
        print(data)  # noqa: T201


if __name__ == "__main__":  # pragma: no cover
    main()
