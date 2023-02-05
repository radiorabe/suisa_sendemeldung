"""Test the suisa_sendemeldung.suisa_sendemeldung module."""
from datetime import date, datetime
from email.message import Message
from os.path import dirname
from unittest.mock import patch

from configargparse import ArgumentParser
from freezegun import freeze_time
from pytest import mark

from suisa_sendemeldung import suisa_sendemeldung


def test_validate_arguments():
    """Test validate_arguments."""

    args = ArgumentParser()
    # length of access_key should be 32
    args.access_key = "iamclearlynotthritytwocharslong"
    # check length of stream_id
    args.stream_id = "iamnot9chars"
    # one output option has to be set (but none is)
    args.csv = False
    args.email = False
    args.stdout = False
    # last_month is in conflict with start_date and end_date
    args.last_month = True
    args.start_date = date(1993, 3, 1)
    with patch("suisa_sendemeldung.suisa_sendemeldung.ArgumentParser") as mock:
        suisa_sendemeldung.validate_arguments(mock, args)
        mock.error.assert_called_once_with(
            "\n"
            "- wrong format on access_key, expected 32 characters but got 31\n"
            "- wrong format on stream_id, expected 9 characters but got 12\n"
            "- no output option has been set, specify one of --csv, --email or --stdout\n"
            "- argument --last_month not allowed with --start_date or --end_date"
        )


def test_parse_date():
    """Test parse_date."""

    # default, "last_month" case
    args = ArgumentParser()
    args.last_month = True
    with freeze_time("1996-04-01"):
        (start_date, end_date) = suisa_sendemeldung.parse_date(args)
    assert start_date == datetime(1996, 3, 1)
    assert end_date == datetime(1996, 3, 31)

    # if no start_date was set, default to 30 days before end_date
    args = ArgumentParser()
    args.last_month = False
    args.start_date = None
    args.end_date = "1996-03-31"
    (start_date, end_date) = suisa_sendemeldung.parse_date(args)
    assert start_date == date(1996, 3, 1)
    assert end_date == date(1996, 3, 31)

    # if no end_date was set, default to today
    args = ArgumentParser()
    args.last_month = False
    args.start_date = False
    args.end_date = False
    with freeze_time("1996-03-31"):
        (start_date, end_date) = suisa_sendemeldung.parse_date(args)
    assert start_date == date(1996, 3, 1)
    assert end_date == date(1996, 3, 31)

    # only specify start_date, selects up to today
    args = ArgumentParser()
    args.last_month = False
    args.start_date = "1996-03-01"
    args.end_date = False
    with freeze_time("1996-04-04"):
        (start_date, end_date) = suisa_sendemeldung.parse_date(args)
    assert start_date == date(1996, 3, 1)
    assert end_date == date(1996, 4, 4)


def test_parse_filename():
    """Test parse_filename."""

    # pass filename from cli
    args = ArgumentParser()
    args.filename = "/foo/bar"
    filename = suisa_sendemeldung.parse_filename(args, None)
    assert filename == "/foo/bar"

    # last_month mode
    args = ArgumentParser()
    args.filename = None
    args.last_month = True
    with freeze_time("1996-03-01"):
        filename = suisa_sendemeldung.parse_filename(args, datetime.now())
    assert (
        filename
        == f"{dirname(suisa_sendemeldung.__file__)}/suisa_sendemeldung_March.csv"
    )

    # start date mode
    args = ArgumentParser()
    args.filename = None
    args.last_month = False
    args.start_date = "1996-03-01"
    with freeze_time("1996-03-01"):
        filename = suisa_sendemeldung.parse_filename(args, datetime.now())
    expected_name = "suisa_sendemeldung_1996-03-01 00:00:00.csv"
    assert filename == f"{dirname(suisa_sendemeldung.__file__)}/{expected_name}"


def test_check_duplicate():
    """Test check_duplicates."""

    # both records are music and not duplicate
    entry_a = {"metadata": {"music": [{"acrid": "123456789"}]}}
    entry_b = {"metadata": {"music": [{"acrid": "987654321"}]}}
    assert not suisa_sendemeldung.check_duplicate(entry_a, entry_b)

    # both records are music and duplicate
    entry_a = {"metadata": {"music": [{"acrid": "123456789"}]}}
    entry_b = {"metadata": {"music": [{"acrid": "123456789"}]}}
    assert suisa_sendemeldung.check_duplicate(entry_a, entry_b)

    # first record is custom and not duplicate
    entry_a = {"metadata": {"custom_files": [{"acrid": "123456789"}]}}
    entry_b = {"metadata": {"music": [{"acrid": "987654321"}]}}
    assert not suisa_sendemeldung.check_duplicate(entry_a, entry_b)

    # first record is custom and duplicate
    entry_a = {"metadata": {"custom_files": [{"acrid": "123456789"}]}}
    entry_b = {"metadata": {"music": [{"acrid": "123456789"}]}}
    assert suisa_sendemeldung.check_duplicate(entry_a, entry_b)

    # second record is custom and not duplicate
    entry_a = {"metadata": {"music": [{"acrid": "123456789"}]}}
    entry_b = {"metadata": {"custom_files": [{"acrid": "987654321"}]}}
    assert not suisa_sendemeldung.check_duplicate(entry_a, entry_b)

    # second record is custom and duplicate
    entry_a = {"metadata": {"music": [{"acrid": "123456789"}]}}
    entry_b = {"metadata": {"custom_files": [{"acrid": "123456789"}]}}
    assert suisa_sendemeldung.check_duplicate(entry_a, entry_b)

    # both records are custom and not duplicate
    entry_a = {"metadata": {"custom_files": [{"acrid": "123456789"}]}}
    entry_b = {"metadata": {"custom_files": [{"acrid": "987654321"}]}}
    assert not suisa_sendemeldung.check_duplicate(entry_a, entry_b)

    # both records are custom and duplicate
    entry_a = {"metadata": {"custom_files": [{"acrid": "123456789"}]}}
    entry_b = {"metadata": {"custom_files": [{"acrid": "123456789"}]}}
    assert suisa_sendemeldung.check_duplicate(entry_a, entry_b)


def test_merge_duplicates():
    """Test merge_duplicates."""

    # check if record_1 reduced to one record and durations are added together
    record_1 = {"metadata": {"music": [{"acrid": "123456789"}], "played_duration": 10}}
    record_2 = {"metadata": {"music": [{"acrid": "987654321"}], "played_duration": 10}}
    raw_records = [record_1, record_1, record_2]
    results = suisa_sendemeldung.merge_duplicates(raw_records)
    assert len(results) == 2
    assert results[0]["metadata"]["played_duration"] == 20


def test_get_csv():
    """Test get_csv."""

    # empty data
    data = []
    csv = suisa_sendemeldung.get_csv(data)
    assert csv == (
        "sep=,\n"
        "Sendedatum,Sendezeit,Sendedauer,Titel,Künstler,Komponist,ISRC,Label\r\n"
    )

    # bunch of data
    data = [
        {
            "metadata": {
                "timestamp_local": "1993-03-01 13:12:00",
                "played_duration": 60,
                "music": [{"title": "Uhrenvergleich"}],
            }
        },
        {
            "metadata": {
                "timestamp_local": "1993-03-01 13:37:00",
                "played_duration": 60,
                "custom_files": [
                    {
                        "title": "Meme Dub",
                        "artist": "Da Gang",
                        "contributors": {
                            "composers": [
                                "Da Composah",
                            ]
                        },
                        "external_ids": {"isrc": "AA6Q72000047"},
                    }
                ],
            }
        },
        {
            "metadata": {
                "timestamp_local": "1993-03-01 16:20:00",
                "played_duration": 60,
                "music": [
                    {
                        "title": "Bubbles",
                        "artists": [
                            {
                                "name": "Mary's Surprise Act",
                            },
                            {
                                "name": "Climmy Jiff",
                            },
                        ],
                        "isrc": "AA6Q72000047",
                        "label": "Jane Records",
                    }
                ],
            }
        },
        {
            "metadata": {
                "timestamp_local": "1993-03-01 17:17:17",
                "played_duration": 60,
                "custom_files": [
                    {
                        "artists": "Artists as string not list",
                    }
                ],
            }
        },
    ]
    csv = suisa_sendemeldung.get_csv(data)
    # pylint: disable=line-too-long
    assert csv == (
        "sep=,\n"
        "Sendedatum,Sendezeit,Sendedauer,Titel,Künstler,Komponist,ISRC,Label\r\n"
        "01/03/93,13:12:00,0:01:00,Uhrenvergleich,,,,\r\n"
        "01/03/93,13:37:00,0:01:00,Meme Dub,Da Gang,Da Composah,AA6Q72000047,\r\n"
        '01/03/93,16:20:00,0:01:00,Bubbles,"Mary\'s Surprise Act, Climmy Jiff","Mary\'s Surprise Act, Climmy Jiff",AA6Q72000047,Jane Records\r\n'
        "01/03/93,17:17:17,0:01:00,,Artists as string not list,Artists as string not list,,\r\n"
    )
    # pylint: enable=line-too-long


def test_create_message():
    """Test create_message."""
    sender = "from@example.org"
    recipient = "long-arm-of-music-industry@example.com"
    subject = "subject"
    text = "text"
    filename = "/tmp/filename"
    csv = "csv"
    carbon_copy = "cc@example.org"
    bcc = "bcc@example.org"

    msg = suisa_sendemeldung.create_message(
        sender, recipient, subject, text, filename, csv, carbon_copy, bcc
    )
    assert msg.get("From") == sender
    assert msg.get("To") == recipient
    assert msg.get("Subject") == subject
    assert msg.get("Cc") == carbon_copy
    assert msg.get("Bcc") == bcc


def test_send_message():
    """Test send_message."""
    msg = Message()

    # no auth
    with patch("suisa_sendemeldung.suisa_sendemeldung.SMTP", autospec=True) as mock:
        suisa_sendemeldung.send_message(msg)
        mock.assert_called_once_with("127.0.0.1")
        ctx = mock.return_value.__enter__.return_value
        ctx.starttls.assert_called_once()
        ctx.send_message.assert_called_once_with(msg)

    # auth, user provided login
    with patch("suisa_sendemeldung.suisa_sendemeldung.SMTP", autospec=True) as mock:
        suisa_sendemeldung.send_message(msg, "127.0.0.1", "user", "password")
        mock.assert_called_once_with("127.0.0.1")
        ctx = mock.return_value.__enter__.return_value
        ctx.starttls.assert_called_once()
        ctx.login.assert_called_once_with("user", "password")

    # auth, user from msg
    with patch("suisa_sendemeldung.suisa_sendemeldung.SMTP", autospec=True) as mock:
        msg.add_header("From", "test@example.org")
        suisa_sendemeldung.send_message(msg, "127.0.0.1", None, "password")
        mock.assert_called_once_with("127.0.0.1")
        ctx = mock.return_value.__enter__.return_value
        ctx.starttls.assert_called_once()
        ctx.login.assert_called_once_with("test@example.org", "password")


@mark.parametrize(
    "test_music,expected",
    [
        ({"external_ids": {"isrc": "AA6Q72000047"}}, "AA6Q72000047"),
        ({"external_ids": {"isrc": ["AA6Q72000047"]}}, "AA6Q72000047"),
        ({"external_ids": {"isrc": "AA 6Q7 20 00047"}}, "AA6Q72000047"),
        ({"external_ids": {"isrc": "ISRCAA6Q72000047"}}, "AA6Q72000047"),
        ({"external_ids": {"isrc": "123456789-1"}}, ""),
        ({"isrc": "AA6Q72000047"}, "AA6Q72000047"),
        ({"isrc": ["AA6Q72000047"]}, "AA6Q72000047"),
        ({"isrc": "ISRCAA6Q72000047"}, "AA6Q72000047"),
        ({"isrc": "AA 6Q7 20 00047"}, "AA6Q72000047"),
        ({"isrc": "123456789-1"}, ""),
    ],
)
def test_get_isrc(test_music, expected):
    """Test get_isrc."""

    isrc = suisa_sendemeldung.get_isrc(test_music)
    assert isrc == expected
