
import mysql.connector


config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',
  'database': 'team073',
  'raise_on_warnings': True,
}


def get_user_pwd(username,password):
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query = "SELECT Username, FirstName, LastName from User where Username = '{user_name}' and Passwd = '{user_pwd}'".format(user_name=username,user_pwd=password)
    cur.execute(query)
    rows = cur.fetchone()
    con.commit()
    con.close()
    return rows

def get_user(username):
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query = "SELECT Username, FirstName, LastName from User where Username = '{user_name}' ".format(user_name=username)
    cur.execute(query)
    rows = cur.fetchone()
    con.commit()
    con.close()
    return rows

def get_user_profile(username):
    query = "select U.Username, U.FirstName, U.LastName, G.Jurisdiction,\
    M.PopulationSize,C.Headquarters,I.JobTitle,I.HiredDate from \
    User U left outer join Gvt_Agency G \
    on U.Username = G.Username \
    left outer join Municipality M \
    on U.Username = M.Username \
    left outer join Company C \
    on U.Username = C.Username \
    left outer join Individual I \
    on U.Username = I.Username \
    where U.Username ='{user}'".format(user=username)
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchone()
    con.commit()
    con.close()
    return rows

def get_owner(username):
    profile = get_user_profile(username)
    return profile[1]+" "+profile[2]

def get_all_esfs():
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query = "SELECT * from ESF ";
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def get_cost_duration():
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query = "SELECT * from CostDuration ";
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def get_next_resource_id():
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query="Select max(ResourceID) from Resources"
    cur.execute(query)
    rows = cur.fetchone()
    con.commit()
    con.close()
    if rows[0] is not None:
        return int(rows[0])+1
    else:
        return 0

def get_next_incident_id():
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query = "SELECT max(IncidentID) from Incident "
    cur.execute(query)
    rows = cur.fetchone()
    con.commit()
    con.close()
    if rows[0] is None:
        return 0
    return rows[0]+1

def insert_resource(resource,user):
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    try:
      query = """INSERT INTO Resources (ResourceID, ResourceName, Model, Time_Cost, Price_Cost, Longitude, Latitude, Username) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')""" %(resource.id,resource.resource_name,resource.model,resource.cost_duration, resource.cost, resource.longitude,resource.latitude,user)
      cur.execute(query)

      query_insert_primaryesf = """INSERT INTO RES_ESF (ResourceID, ESFId, PrimaryESFInd) VALUES ('%s', '%s', 'Y')""" %(resource.id,resource.primary_esf)
      cur.execute(query_insert_primaryesf)

      for esf in resource.additional_esfs:
         query_insert_secesf = """INSERT INTO RES_ESF (ResourceID, ESFId) VALUES ('%s', '%s')""" %(resource.id,esf)
         cur.execute(query_insert_secesf)

      for capability in resource.capabilities.split('\n'):
         query_insert_capability = """INSERT INTO Capabilities (ResourceID, Capability) VALUES ('%s', '%s')""" %(resource.id,capability)
         print query_insert_capability
         cur.execute(query_insert_capability)

    except Exception as e:
      print "Unable to insert resource in the db:",e
      raise Exception('Add Resource Failed!')


    con.commit()
    con.close()

def get_all_incidents(username):
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query = "SELECT IncidentID,Description from Incident where Username = '{user_name}' ".format(user_name=username);
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def insert_incident(incident,user):
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    try:
      query = """INSERT INTO Incident (IncidentID, IncidentDate, Description, Longitude, Latitude, Username) VALUES ('%s','%s','%s','%s','%s','%s')""" %(incident.incident_id,incident.date,incident.description, incident.longitude,incident.latitude,user)
      print query
      cur.execute(query)

    except Exception as e:
      print "Unable to insert incident in the db:",e
      raise Exception('Add Incident Failed!')


    con.commit()
    con.close()

def new_search(search):
    if int(search.incident_id) > 0:
        full_with_incident = """select Resource_Distance.ResourceID, Resource_Distance.ResourceName,Resource_Distance.Owner, Resource_Distance.Cost, Resource_Distance.NextAvailableDate,Resource_Distance.Status,Resource_Distance.Res_Distance from
(Select Resources.ResourceID, Resources.ResourceName,CONCAT(FirstName,' ',LastName) as Owner, CONCAT(Price_Cost,'/',Time_Cost) as Cost ,
CASE  WHEN Repairs.StartDate <= CURDATE() and Repairs.EndDate > CURDATE() THEN Repairs.EndDate WHEN RR.Status_State='Deployed'
and RR.EndDate > CURDATE()  THEN RR.EndDate  ELSE 'NOW' END as NextAvailableDate,   CASE  WHEN Repairs.StartDate <= CURDATE()
and Repairs.EndDate > CURDATE() THEN 'IN REPAIR' WHEN RR.Status_State='Deployed' and RR.EndDate > CURDATE()  THEN 'NOT AVAILABLE'
ELSE 'AVAILABLE' END as Status,
I.IncidentID, @A := ABS(RADIANS(Resources.Latitude) - RADIANS(I.Latitude)) , @B := ABS(RADIANS(Resources.Longitude) - RADIANS(I.Longitude))  , @C := ABS((POWER(SIN(@A /2),2) + COS(I.Latitude))     * COS(RADIANS(Resources.Latitude))* POWER(SIN(@B /2),2)) , @D := 2 * ATAN2(SQRT(@C), SQRT(1-@C))  ,
6371*@D AS Res_Distance
from Resources cross join Incident I
inner join User on  User.Username = Resources.Username
left outer join Repairs on Repairs.ResourceID = Resources.ResourceID
left outer join (select * from Resource_Requested where Status_State='Deployed')RR on RR.ResourceID = Resources.ResourceID
where  I.IncidentID = {incident_id}  and Resources.ResourceID not in (
select ResourceID from Resource_Requested where IncidentID = {incident_id} and Status_State='Closed'
)
)Resource_Distance where Res_Distance <= {distance} """

        keyword_filter = """ and Resource_Distance.ResourceID   in ( select Resources.ResourceID from Resources left outer join Capabilities  on Resources.ResourceID = Capabilities.ResourceID where Capability like \'%{keyword}%\' or ResourceName like \'%{keyword}%\' or Model like \'%{keyword}%\' \
            group by Resources.ResourceID,Resources.ResourceName)"""

        esf_filter = """ and Resource_Distance.ResourceID in (select resourceid from res_esf where primaryesfind= 'Y' and esfid = {esf_id} \
)"""

        if search.esf >0:

            query = full_with_incident+esf_filter

            if search.keyword:
                query = query+keyword_filter
                query = query.format(keyword = search.keyword,esf_id=search.esf,incident_id=search.incident_id,distance=search.location)
            else:
                query = query.format(esf_id=search.esf,incident_id=search.incident_id,distance=search.location)

        elif search.keyword:
            query = full_with_incident+keyword_filter
            query = query.format(keyword = search.keyword,incident_id=search.incident_id,distance=search.location)

        else:
            query = full_with_incident
            query = query.format(incident_id=search.incident_id,distance=search.location)

        order_clause = " ORDER BY Res_Distance, Resource_Distance.ResourceName "
        query = query+order_clause
        print query


    else:
        full_search_query = """Select Resources.ResourceID, Resources.ResourceName,CONCAT(FirstName,' ',LastName) as Owner, CONCAT(Price_Cost,'/',Time_Cost) as Cost ,
CASE  WHEN Repairs.StartDate <= CURDATE() and Repairs.EndDate > CURDATE() THEN Repairs.EndDate WHEN RR.Status_State='Deployed'
and RR.EndDate > CURDATE()  THEN RR.EndDate  ELSE 'NOW' END as NextAvailableDate,   CASE  WHEN Repairs.StartDate <= CURDATE()
and Repairs.EndDate > CURDATE() THEN 'IN REPAIR' WHEN RR.Status_State='Deployed' and RR.EndDate > CURDATE()  THEN 'NOT AVAILABLE'
ELSE 'AVAILABLE' END as Status from Resources
inner join User on  User.Username = Resources.Username
left outer join Repairs on Repairs.ResourceID = Resources.ResourceID
left outer join (select * from Resource_Requested where Status_State='Deployed')RR on RR.ResourceID = Resources.ResourceID
"""
        keyword_filter = """ Resources.ResourceID   in ( select Resources.ResourceID from Resources left outer join Capabilities  on Resources.ResourceID = Capabilities.ResourceID where Capability like \'%{keyword}%\' or ResourceName like \'%{keyword}%\' or Model like \'%{keyword}%\' \
            group by Resources.ResourceID,Resources.ResourceName)"""

        if search.esf >0:
            esf_filter = """ Resources.ResourceID in (select resourceid from res_esf where primaryesfind= 'Y' and esfid = {esf_id} \
)"""
            query = full_search_query+" where "+esf_filter

            if search.keyword:
                query = query+" and "+keyword_filter
                query = query.format(keyword = search.keyword,esf_id=search.esf,incident_id=search.incident_id,distance=search.location)
            else:
                query = query.format(esf_id=search.esf,incident_id=search.incident_id,distance=search.location)

        elif search.keyword:
            query = full_search_query+" where "+keyword_filter
            query = query.format(keyword = search.keyword,incident_id=search.incident_id,distance=search.location)

        else:
            query =  full_search_query

        print query


    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows


def resources_in_use(user_id):
    stmt = "select Resources.ResourceID, ResourceName,Description,CONCAT(FirstName,' ',LastName) as Owner,StartDate,EndDate,Incident.IncidentID from Incident \
 inner join Resource_Requested \
 on Incident.IncidentID = Resource_Requested.IncidentID \
 inner join  Resources \
 on Resource_Requested.ResourceID = Resources.ResourceID \
 inner join User \
 on Resources.Username = User.Username \
 where Incident.Username = '{current_user}' and Resource_Requested.Status_State='Deployed' and Resource_Requested.EndDate > CURDATE()"
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query  = stmt.format(current_user=user_id);
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def resources_requested(user_id):
    stmt = "select Resources.ResourceID, ResourceName,Description,CONCAT(FirstName,' ',LastName) as Owner,EndDate,Incident.IncidentID  from Resource_Requested \
 inner join Incident \
 on Incident.IncidentID = Resource_Requested.IncidentID \
 inner join  Resources \
 on Resource_Requested.ResourceID = Resources.ResourceID\
 inner join User\
 on Resources.Username = User.Username\
 where Incident.Username = '{current_user}'\
 and Resource_Requested.Status_State='Open' "
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query  = stmt.format(current_user=user_id);
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def resources_recieved(user_id):
    stmt = " select Resources.ResourceID, ResourceName,Description,CONCAT(FirstName,' ',LastName) as Requestor,Resource_Requested.Enddate,Incident.IncidentID,\
 CASE WHEN  Resource_Requested.EndDate > CURDATE() and Resource_Requested.Status_State='Deployed' THEN 'In Use' \
 WHEN Repairs.StartDate <= CURDATE()  and Repairs.Enddate > CURDATE() THEN 'In Repair' END As Action \
 from Resources\
 left outer join Repairs\
 on Repairs.ResourceID = Resources.ResourceID\
 inner join Resource_Requested on Resources.ResourceID = Resource_Requested.ResourceID \
 inner join Incident \
 on Incident.IncidentID = Resource_Requested.IncidentID  \
 inner join User \
 on Incident.Username = User.Username where Resources.Username = '{current_user}' \
 and Resource_Requested.Status_State='Open' "

    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query  = stmt.format(current_user=user_id);
    print query
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def resources_in_repair(user_id):
    stmt = "Select Repairs.ResourceID, Resources.ResourceName,Repairs.RepairId,Repairs.StartDate, Repairs.EndDate, Case when Repairs.StartDate > CURDATE() THEN 'Cancel' ELSE 'InRepair' END AS Action from Repairs \
 inner join Resources\
 on Repairs.ResourceID = Resources.ResourceID\
 inner join User\
 on Resources.Username = User.Username where Resources.Username = '{current_user}' \
 and Repairs.Enddate > CURDATE() order by Repairs.RepairId"
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query  = stmt.format(current_user=user_id);
    print query
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def resource_report(user_id):
    stmt = "select ESF.ESFId, ESF.ESFDescription, cr, ci from \
    ESF left outer join (select t.esfid,t.ESFDescription , sum(a) as cr ,sum(b) as ci from\
    (select res_esf.esfid,esf.esfdescription ,count(res_esf.ResourceID) as a, 0 as b from resources\
    inner join res_esf\
    on resources.resourceid = res_esf.resourceid\
    inner join esf\
    on res_esf.esfid = esf.esfid\
    where username='{current_user}' and PrimaryESFInd = 'Y'\
    group by res_esf.esfid, esf.esfdescription\
    union\
    select res_esf.esfid,esf.esfdescription ,0,count(res_esf.ResourceID) as b  from resource_requested\
    inner join  resources\
    on resource_requested.resourceid = resources.resourceid\
    inner join res_esf on\
    resource_requested.resourceid = res_esf.ResourceID\
    inner join esf on\
    esf.ESFId = res_esf.esfid\
    where \
    resources.username='{current_user}'and\
    status_state='Deployed' and enddate >= curdate()\
    and primaryesfind='Y'\
    group by res_esf.esfid, esf.esfdescription) t\
    group by t.esfid, t.ESFDescription ) temp2 \
    on ESF.ESFId = temp2.ESFId"

    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query  = stmt.format(current_user=user_id);
    print query
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def resource_report_totals(user_id):
    stmt = "select sum(res_count),sum(use_count)\
    from (select t.esfid,t.ESFDescription , sum(a) as res_count ,sum(b) as use_count from\
    (select res_esf.esfid,esf.esfdescription ,count(res_esf.ResourceID) as a, 0 as b from resources\
    inner join res_esf\
    on resources.resourceid = res_esf.resourceid\
    inner join esf\
    on res_esf.esfid = esf.esfid\
    where username='{current_user}' and PrimaryESFInd = 'Y'\
    group by res_esf.esfid, esf.esfdescription\
    union\
    select res_esf.esfid,esf.esfdescription ,0,count(res_esf.ResourceID) as b  from resource_requested\
    inner join  resources\
    on resource_requested.resourceid = resources.resourceid\
    inner join res_esf on\
    resource_requested.resourceid = res_esf.ResourceID\
    inner join esf on\
    esf.ESFId = res_esf.esfid\
    where \
    resources.username='{current_user}'and\
    status_state='Deployed' and enddate >= curdate()\
    and primaryesfind='Y'\
    group by res_esf.esfid, esf.esfdescription) t\
    group by t.esfid, t.ESFDescription) count_table"

    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query  = stmt.format(current_user=user_id);
    cur.execute(query)
    print query
    rows = cur.fetchone()
    con.commit()
    con.close()
    return rows

def request_resource_db(resource):
    query = """INSERT INTO Resource_Requested \
    (ResourceID, IncidentID, StartDate, EndDate, Status_State) \
    VALUES(%s, %s, '%s', '%s', '%s') """ %(resource.resource_id, resource.incident, resource.start_date, resource.return_by,"Open")

    print query

    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

def deploy_resource_db(resource):
    query =  """UPDATE Resource_Requested \
    SET  Status_State='Deployed' \
    WHERE IncidentID=%s AND ResourceID=%s  and Status_State='Open' """ %(resource.incident,resource.resource_id)
    print query
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

def repair_resource_db(resource):
    query = """INSERT INTO Repairs \
(StartDate, EndDate, ResourceID) \
VALUES('%s', '%s', %s) """%(resource.start_date,resource.return_by,resource.resource_id)
    print query
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

def cancel_repair_db(resource):
    query = """ DELETE FROM  Repairs \
    WHERE RepairId=%s AND ResourceID=%s """%(resource.incident,resource.resource_id)
    print query
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

def cancel_request_db(resource):
    query = """ DELETE FROM Resource_Requested \
    WHERE IncidentID=%s AND ResourceID=%s """%(resource.incident,resource.resource_id)
    print query
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

def return_request_db(resource):
    query =  """UPDATE Resource_Requested \
    SET  Status_State='Closed' \
    WHERE IncidentID=%s AND ResourceID=%s  and Status_State='Deployed' """ %(resource.incident,resource.resource_id)
    print query
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()


def reject_request_db(resource):
    query = """UPDATE Resource_Requested \
    SET  Status_State='Rejected' \
    WHERE IncidentID=%s AND ResourceID=%s  and Status_State='Open' """ %(resource.incident,resource.resource_id)
    print query
    con = mysql.connector.connect(**config)
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

def resource_summary(user_id):
    stmt =  "select Resources.ResourceID, ResourceName, CASE WHEN  RR.EndDate > CURDATE() and RR.Status_State='Deployed' THEN 'In Use'  WHEN Repairs.StartDate <= CURDATE()  and Repairs.Enddate > CURDATE() THEN 'In Repair'  ELSE 'Available' END As Action  from Resources \
    left outer join Repairs on Repairs.ResourceID = Resources.ResourceID \
    left outer join (Select * from Resource_Requested where Status_State='Open' or Status_State='Deployed')RR on Resources.ResourceID = RR.ResourceID\
    where Resources.Username = '{current_user}' \
     order by Resources.ResourceID "

    con = mysql.connector.connect(**config)
    cur = con.cursor()
    query  = stmt.format(current_user=user_id);
    print query
    cur.execute(query)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows
