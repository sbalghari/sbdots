import pytest
from sbdots.library.notify import Notification


class TestNotification:
    """Tests for notify module"""

    def test_notification_initialization(self):
        """Test Notification can be initialized with basic parameters"""
        notif = Notification(title="Test", body_text="Test message")
        assert notif.title == "Test"
        assert notif.body_text == "Test message"
        assert notif.urgency_level == "normal"

    def test_notification_with_custom_urgency(self):
        """Test Notification with custom urgency level"""
        notif = Notification(
            title="Test", body_text="Test", urgency_level="critical"
        )
        assert notif.urgency_level == "critical"

    def test_notification_with_expiry_time(self):
        """Test Notification expiry time conversion to milliseconds"""
        notif = Notification(title="Test", body_text="Test", expire_time=10)
        assert notif.expiry_time == 10000

    def test_notification_with_progression(self):
        """Test Notification with progression enabled"""
        notif = Notification(title="Test", body_text="Test", progression=True)
        assert notif.progression is True

    def test_notification_invalid_urgency_level(self):
        """Test Notification raises error for invalid urgency level"""
        with pytest.raises(ValueError):
            Notification(
                title="Test", body_text="Test", urgency_level="invalid_level"
            )

    def test_notification_build_cmd(self):
        """Test _build_cmd creates proper notify-send command"""
        notif = Notification(title="Test", body_text="Message")
        cmd = notif._build_cmd()
        assert "notify-send" in cmd
        assert "Test" in cmd
        assert "Message" in cmd
        assert "SBDOTS" in cmd
