Sloth CI extension that adds an SMTP handler to the build logger in Sloth CI apps.

.. warning::

    This extension uses the default Python SMTPHandler from logging.handlers. SMTPHandler doesn't work with GMail's SMTP because it creates an smtplib.SMTP object to connect to the host, whereas GMail requires smtplib.SMTP_SSL.

    Outlook.com is approved to work fine.

Extension params::

    # Use the module sloth-ci.ext.build_email_notifications.
    module: build_email_notifications

    # Emails to send the notifications to.
    emails:
        - foo@bar.com
        - admin@example.com

    # Log level (number or valid Python logging level name).
    # ERROR includes only build fails, WARNING adds partial completions,
    # INFO adds completion, and DEBUG adds trigger notifications.
    # Default is WARNING.
    level: INFO

    # The "from" address in the emails. Default is "build@sloth.ci."
    from: notify@example.com

    # The email subject on build trigger. You can use the {listen_point} placeholder.
    # Default is "{listen_point}: Build Triggered."
    subject_triggered: 'Triggered build on {listen_point}!'

    # The email subject on build completion.You can use the {listen_point} placeholder.
    # Default is "{listen_point}: Build Completed."
    subject_completed: 'Hooray! {listen_point} works!'

    # The email subject on build partial completion. You can use the {listen_point} placeholder.
    # Default is "{listen_point}: Build Partially Completed."
    subject_partially_completed: 'Better than nothing on {listen_point}'

    # The email subject on build fail. You can use the {listen_point} placeholder.
    # Default is "{listen_point}: Build Failed."
    subject_failed: 'Fail on {listen_point}'

    # SMTP settings.
    # SMTP mail host and (if not default) port.
    # Mandatory parameter.
    mailhost: 'smtp-mail.outlook.com:25'

    # SMTP login.
    login: foo@bar.baz

    # SMTP password.
    password: bar

    # If the SMTP server requires TLS, set this to true. Default is false.
    # If necessary, you can provide a keyfile name or a keyfile and a certificate file names.
    # This param is used only the login and password params are supplied.
    secure: true
    # secure:
    #    -   keyfile
    #    -   cerfile


