import reflex as rx

# class LogitConfig(rx.Config):
#     pass

config = rx.Config(
    app_name="logit",
    db_url="sqlite:///data.db",
    api_url="http://192.168.1.28:3988",
    # backend_port="4000"
    # cors_allowed_origins=
)