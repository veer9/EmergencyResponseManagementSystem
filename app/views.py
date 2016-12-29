from flask import Flask, request, redirect, render_template, session , flash,json
from flask_login import ( login_required, login_user,
                         current_user, logout_user, UserMixin)

from datetime import timedelta
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer
from app import app
from wtforms import Form
from forms import LoginForm,NewResourceForm,IncidentInfoForm,SearchResourceForm
from user import User,Resource,ERMSError,Profile,Incident,Search,SearchResults,ReportResults,ResourceAction,ResourceStatus
from models import (insert_resource,get_user_profile,get_all_incidents,insert_incident,
    resource_report,resources_in_repair,resources_recieved,resources_requested,resources_in_use,
    resource_report_totals,request_resource_db,deploy_resource_db,repair_resource_db,cancel_repair_db,cancel_request_db,
    reject_request_db,return_request_db,get_owner,get_cost_duration,resource_summary,new_search)
from wtforms.ext.appengine.db import model_form
from datetime import timedelta,date,datetime

app.secret_key = "a_random_secret_key_$%#!@"
login_serializer = URLSafeTimedSerializer(app.secret_key)

login_manager = LoginManager()
login_manager.login_view = "/ulogin/"
#Setup the login manager.
login_manager.setup_app(app)
login_manager.init_app(app)



@login_manager.user_loader
def load_user(userid):
    """
    Flask-Login user_loader callback.
    The user_loader function asks this function to get a User Object or return
    None based on the userid.
    The userid was stored in the session environment by Flask-Login.
    user_loader stores the returned User object in current_user during every
    flask request.
    """
    return User.get(userid)


@app.route("/logout/")
def logout_page():
    """
    Web Page to Logout User, then Redirect them to Index Page.
    """
    logout_user()
    return redirect("/")

@app.route("/ulogin/", methods=["GET", "POST"])
def login_page():
    """
    Web Page to Display Login Form and process form.
    """
    form = LoginForm(request.form)
    if request.method == "POST":
        user = User.get_unpwd(form.username.data,form.password.data)
        #user = User.get(form.username.data)
        if user is not None:
            login_user(user, remember=True)
            return redirect(request.args.get("next") or "/")
        else:
            flash('Invalid Username or Password!')
    return render_template("userlogin.html",form = form)

@app.route("/")
def index_page():
    """
    Web Page to display The Main Index Page
    """
    user_id = (current_user.get_id() or "Anonymous User")
    return render_template("index.html", user_id=user_id)

@app.route("/profile")
@login_required
def profile_page():
    """
    Web Page to display The Profile Index Page
    """

    profile = get_user_profile(current_user.get_id())
    user_profile = Profile(profile[0],profile[1],profile[2],profile[3],profile[4],profile[5],profile[6])
    #form = model_form(user_profile, UserProfileForm)

    user_id = current_user.get_id()
    records = resource_summary(user_id)
    results=[]
    for record in records:
        value = ResourceStatus(record[0],record[1],None,None,None,None,record[2],None)
        results.append(value)
    #return render_template("profile.html",records=results)

    return render_template("profile.html", form=user_profile,records=results)


@app.route("/add_resources/",methods=["GET", "POST"])
@login_required
def add_resources():
    form = NewResourceForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
             flash('Recieved Add Resource Request')
             d = {}
             duration_list=get_cost_duration()
             for x, y in duration_list:
                 d.setdefault(x, []).append(y)
             res = Resource(form.resource_id.data,form.resource_name.data,form.primary_esf.data,form.additional_esfs.data,form.model.data, form.capabilities.data,repr(form.latitude.data),repr(form.longitude.data),form.cost.data,d.get(form.cost_duration.data)[0])
             insert_resource(res,current_user.get_id())
             flash('Resouce successfully added to the DB!')
    owner = get_owner(current_user.get_id())
    return render_template("resources.html", form=form,owner=owner)

@app.route("/add_incidents/",methods=["GET", "POST"])
@login_required
def add_incidents():
    form=IncidentInfoForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
            flash('New Incident added!')
            incident = Incident(form.incident_id.data,form.date.data,form.description.data,repr(form.longitude.data),repr(form.latitude.data))
            insert_incident(incident,current_user.get_id())
            return render_template("incidents.html", form = form)
    return render_template("incidents.html", form = form)

@app.route("/search/",methods=["GET", "POST"])
@login_required
def search():

    incident_list = get_all_incidents(current_user.get_id())
    incident_list.insert(0,(0, u' - select an option -'))
    d = {}
    for x, y in incident_list:
      d.setdefault(x, []).append(y)
    form = SearchResourceForm(incident_list)
    if request.method == "POST":
         #flash('Searching!')
         if form.location.data is None:
             form.location.data = 50000
         search = Search(form.keyword.data,form.esf.data,form.location.data,form.incident_list.data)
         results = new_search(search)

         search_results = []
         all_columns=None
         if int(search.incident_id) > 0:
            incident_desc=d.get(int(search.incident_id))[0]+'(' + search.incident_id + ')'
         else:
            incident_desc = None
         for record in results:
            if int(search.incident_id) > 0 and search.location >0:
                all_columns="display"

                incident_desc=d.get(int(search.incident_id))[0]+'(' + search.incident_id + ')'

                action="Request"
                if record[5] == "IN REPAIR":
                    action = None
                elif record[5] == "AVAILABLE" and record[2].startswith(current_user.FirstName) :
                    action = "Deploy-Repair"
                val = SearchResults(record[0],record[1],record[2],record[3],record[4],record[5],record[6],action)
            else:
                val = SearchResults(record[0],record[1],record[2],record[3],record[4],record[5],None,None)
            search_results.append(val)
         #flash('Search Complete!')
         return render_template("search.html",form = form,records=search_results,all_columns=all_columns,incident_id=search.incident_id ,incident_desc=incident_desc)
    return render_template("search.html",form = form,records=None)

@app.route("/resource_status/",methods=["GET", "POST"])
@login_required
def resource_status():
    user_id = current_user.get_id()
    in_use = resources_in_use(user_id)
    inuse_results =[]
    for record in in_use:
        value = ResourceStatus(record[0],record[1],record[2],record[3],record[4],record[5],"Return",record[6])
        inuse_results.append(value)

    res_req = resources_requested(user_id)
    resreq_results = []
    for record in res_req:
        value = ResourceStatus(record[0],record[1],record[2],record[3],record[4],None,"CancelRequest",record[5])
        resreq_results.append(value)

    res_res = resources_recieved(user_id)
    resres_results = []
    for record in res_res:

        action="Deploy-Reject"
        if record[4]=="Deployed":
            action="Reject"
        value = ResourceStatus(record[0],record[1],record[2],record[3],record[4],record[5],action,None)
        resres_results.append(value)

    res_repair = resources_in_repair(user_id)
    resrepair_results = []
    for record in res_repair:

        value = ResourceStatus(record[0],record[1],record[2],None,record[3],record[4],record[5],None)

        resrepair_results.append(value)

    return render_template("resource_status.html",inuse=inuse_results,requested=resreq_results,recieved=resres_results,repairs=resrepair_results)

@app.route("/reports/",methods=["GET", "POST"])
@login_required
def reports():
    user_id = current_user.get_id()
    records = resource_report(user_id)
    results=[]
    for record in records:
        value = ReportResults(record[0],record[1],record[2],record[3])
        results.append(value)
    total_record = resource_report_totals(user_id)
    value = ReportResults("", "TOTALS",total_record[0],total_record[1])
    results.append(value)
    return render_template("reports.html",records=results)


@app.route("/pass_through/",methods=["GET","POST"])
def pass_through():
    if request.method == "POST":
        return json.dumps({'status':'OK','user':'user','pass':'password'});

@app.route("/request_resource/",methods=["GET","POST"])
def request_resource():
    if request.method == "POST":
        resource = ResourceAction(request.form['resource-id'],request.form['incident-id'],request.form['start-date'],request.form['end-date'])
        request_resource_db(resource)
        return json.dumps({'status':'OK'});

@app.route("/repair_resource/",methods=["GET","POST"])
def repair_resource():
    if request.method == "POST":
        date_1 =  request.form['r-start-date']
        days = request.form['repair-days']

        if date_1 == 'NOW':
            date_object = datetime.now().date()
        else:
            date_object = datetime.strptime(date_1, '%Y-%m-%d')
        d = date_object + timedelta(days=int(days))
        resource = ResourceAction(request.form['r-resource-id'],None,date_object,d)
        repair_resource_db(resource)
        return json.dumps({'status':'OK'});

@app.route("/cancel_repair/",methods=["GET","POST"])
def cancel_repair():
    if request.method == "POST":
        resource = ResourceAction(request.form['resource-id'],request.form['repair-id'],None,None)
        cancel_repair_db(resource)
        return json.dumps({'status':'OK'});

@app.route("/cancel_request/",methods=["GET","POST"])
def cancel_request():
    if request.method == "POST":
        resource = ResourceAction(request.form['resource-id'],request.form['incident-id'],None,None)
        cancel_request_db(resource)
        return json.dumps({'status':'OK'});

@app.route("/return_request/",methods=["GET","POST"])
def return_request():
    if request.method == "POST":

        resource = ResourceAction(request.form['resource-id'],request.form['incident-id'],None,None)
        return_request_db(resource)
        return json.dumps({'status':'OK'});

@app.route("/reject_request/",methods=["GET","POST"])
def reject_request():
    if request.method == "POST":

        resource = ResourceAction(request.form['resource-id'],request.form['incident-id'],None,None)
        reject_request_db(resource)
        return json.dumps({'status':'OK'});

@app.route("/deploy_resource/",methods=["GET","POST"])
def deploy_resource():
    if request.method == "POST":

        resource = ResourceAction(request.form['resource-id'],request.form['incident-id'],None,None)
        deploy_resource_db(resource)
        return json.dumps({'status':'OK'});

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(505)
def page_not_found(e):
    return render_template('500.html'), 500
