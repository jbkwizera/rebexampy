from flask import render_template, flash
from app import app
from app.forms import RegIDForm

from bs4 import BeautifulSoup
import requests
import re

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    resu = False
    form = RegIDForm()
    if form.validate_on_submit():
        level = form.level.data
        regid = form.regid.data
        who   = form.who.data

        validate_regid = {
            "P3": ["^[0-9]{15}$", "http://results.reb.rw/retrieveplMarks.aspx?id=" + regid + "&le=P3"],
            "S3": ["^[0-9]{7}[a-zA-Z]{3}[0-9]{7}$", "http://results.reb.rw/retrieveolMarks.aspx?id=" + regid + "&le=S3"],
            "S6": ["^[0-9]{4}[a-zA-Z0-9]{2,3}[a-zA-Z]{3}[0-9]{7}$", "http://results.reb.rw/retrieveMarks.aspx?id=" + regid + "&le=S6"]
        }
        flash(f"Data Requested for ID {regid}, level {level}, who {who}")

        # Fetch all the stuff
        resu = fetch_results(level, regid, who, validate_regid, form)
        if resu:
            resu = sorted(resu, key=lambda item: int(item["candidate_info"]["aggregate"]), reverse=True)
    return render_template("index.html", form=form, resu=resu)

def student_results(level, regid, who, validate_regid):
    r = requests.get(validate_regid[level][1])
    if "No results available" in r.text:
        return False
    soup = BeautifulSoup(r.text, features="html.parser")
    info_rws = soup.find("table", attrs={"id": "candinfos"}).find_all("tr")
    resu_rws = soup.find("table", attrs={"id": "results"}).find_all("tr")
    info_dct = {}
    resu_dct = {}

    info_dct["name"]      = info_rws[0].find_all("td")[1].text;
    info_dct["gender"]    = info_rws[0].find_all("td")[4].text;
    info_dct["mention"]   = info_rws[1].find_all("td")[4].text;
    info_dct["aggregate"] = info_rws[2].find_all("td")[4].text;

    resu_dct["courses"] = [item.text for item in resu_rws[0].find_all("th")]
    resu_dct["grades"]  = [item.text for item in resu_rws[1].find_all("td")]
    return {"candidate_info": info_dct, "candidate_resu": resu_dct}

def fetch_results(level, regid, who, validate_regid, form):
    if not re.search(validate_regid[level][0], regid):
        form.regid.errors = ["Not a valid choice"]
        return False

    if who.lower() == "me":
        ret = student_results(level, regid, who, validate_regid)
        return [ret] if ret else False

    base = regid[:10]
    year = regid[13:]
    patl = len(regid)
    ret  = []
    no   = 0
    while True:
        no += 1
        regid = base + str(no).zfill(3) + year
        validate_regid[level][1] = re.sub(f"=[a-zA-Z0-9]{{{patl}}}", f"={regid}", validate_regid[level][1])
        res = student_results(level, regid, who, validate_regid)
        if not res: break
        ret.append(res)
    return ret
