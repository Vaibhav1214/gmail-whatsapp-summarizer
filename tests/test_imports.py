def test_project_imports():
    """Verify that all project modules and custom tools import successfully."""
    import config
    import gmail_tools
    import main
    import whatsapp_tools

    # Confirm Pydantic validation initialized setting values successfully
    assert config.settings.GMAIL_EMAIL is not None
    assert str(config.settings.GMAIL_EMAIL).strip() != ""
    assert config.settings.TWILIO_FROM_NUMBER is not None
    assert config.settings.TWILIO_TO_NUMBER is not None

    # Reference the custom tools/functions to satisfy unused import linters
    assert gmail_tools.fetch_recent_emails_from_inbox is not None
    assert whatsapp_tools.send_whatsapp_message is not None
    assert main.main is not None
