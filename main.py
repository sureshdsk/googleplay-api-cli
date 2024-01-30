import json
import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from gpapi.googleplay import GooglePlayAPI, RequestError
from util import load_credential_from_file, AppAvailability


app = typer.Typer()
console = Console()


@app.command()
def login(email: Annotated[str, typer.Argument(envvar="GPLAY_EMAIL")],
          password: Annotated[str, typer.Argument(envvar="GPLAY_PASSWORD")], ):
    print("Initiating login..")
    api = GooglePlayAPI(locale="en_US", timezone="UTC", device_codename="walleyebacon")
    api.login(email=email, password=password)
    auth_response = {
        "RefreshToken": api.authSubToken,
        "GsfId": api.gsfId
    }
    with open('gp_token.json', 'w+') as f:
        f.write(json.dumps(auth_response))
    print("Token saved successfully.")


@app.command()
def search(query: str):
    gp_credential = load_credential_from_file()
    api = GooglePlayAPI(locale="en_US", timezone="UTC", device_codename=gp_credential.device_code_name)
    api.login(gsfId=gp_credential.gsf_id, authSubToken=gp_credential.auth_sub_token)

    result = api.search(query)

    if len(result) and len(result[0]['child']) and len(result[0]['child'][0]['child']):
        table = Table(title=f"Search result for {query}")
        table.add_column("Title")
        table.add_column("Package Name")
        table.add_column("Version", style="green")
        table.add_column("VersionCode", style="green")
        table.add_column("Upload Date")

        for app_result in result[0]['child'][0]['child']:
            title = app_result['title']
            package_name = app_result['docid']
            app_detail = app_result['details']['appDetails']
            version = app_detail['versionString']
            version_code = str(app_detail['versionCode'])
            upload_date = app_detail['uploadDate']

            table.add_row(title, package_name, version, version_code, upload_date)
        console.print(table)
    else:
        console.print("No result")


@app.command()
def get_app(package_name: Annotated[str, typer.Argument()]):
    gp_credential = load_credential_from_file()
    api = GooglePlayAPI(locale="en_US", timezone="UTC", device_codename=gp_credential.device_code_name)

    api.login(gsfId=gp_credential.gsf_id, authSubToken=gp_credential.auth_sub_token)
    try:
        app_result = api.details(package_name)
        title = app_result['title']
        package_name = app_result['docid']
        app_detail = app_result['details']['appDetails']
        version = app_detail.get('versionString')
        version_code = str(app_detail.get('versionCode'))
        upload_date = app_detail['uploadDate']
        downloads = app_detail['numDownloads']
        availability = AppAvailability.from_int(app_result['availability']['restriction'])

        table = Table(title=f"Result for {package_name}", style="cyan")
        table.add_column(package_name)
        table.add_row("Title", title)
        table.add_row("Package Name", package_name)
        table.add_row("Version", version)
        table.add_row("Version Code", version_code)
        table.add_row("Upload Date", upload_date)
        table.add_row("Downloads", downloads)
        table.add_row("Availability", availability.name)

        console.print(table)
    except RequestError as err:
        if err.value == "Item not found.":
            console.print("App not found..")
            typer.Exit()


@app.command()
def download(package_name: Annotated[str, typer.Argument()]):
    gp_credential = load_credential_from_file()
    api = GooglePlayAPI(locale="en_US", timezone="UTC", device_codename=gp_credential.device_code_name)
    api.login(gsfId=gp_credential.gsf_id, authSubToken=gp_credential.auth_sub_token)
    app_result = api.details(package_name)
    app_detail = app_result['details']['appDetails']
    version_code = app_detail['versionCode']
    console.print(f"Downloading...")
    download_result = api.download(package_name, versionCode=version_code)

    file_name = f"downloads/{package_name}_{version_code}" + ".apk"
    with open(file_name, "wb") as apk_file:
        for chunk in download_result.get("file").get("data"):
            apk_file.write(chunk)
    console.print(f"APK saved at {file_name}")


if __name__ == "__main__":
    app()
