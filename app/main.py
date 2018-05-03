from create_app import create_app

app = create_app()

if __name__ == "__main__":
        app.run(host=app.config["HOST"],
                port=app.config["PORT"],
                workers=app.config["WORKERS"],
                debug=(app.config["API_ENV"] != "PRODUCTION"))
