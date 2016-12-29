from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import md5
from app import app
from models import get_user,get_user_pwd

class Search():
    def __init__(self, keyword,esf,location,incident_id):
        self.keyword = keyword
        self.esf = esf
        self.location = location
        self.incident_id = incident_id

    def get_id(self):
        return self.uid

    def set(self,list):
        self.incident_list = list

    def __repr__(self):
        return "<List '{}'>".format(self.list)

    def __html__(self):
        return repr(self)

class SearchResults():
    def __init__(self, resource_id,resource_name,owner,cost,nextAvailableDate,status,distance,action):
        self.resource_id = resource_id
        self.resource_name = resource_name
        self.owner = owner
        self.cost = cost
        self.nextAvailableDate = nextAvailableDate
        
        self.status = status
        self.distance = distance
        self.action = action

    def get_id(self):
        return self.resource_id

    def __repr__(self):
        return "<List '{}'>".format(self.list)

    def __html__(self):
        return repr(self)



class User(UserMixin):
    """
    User Class for flask-Login
    """
    def __init__(self, userid, FirstName , LastName ):
        self.id = userid
        self.FirstName = FirstName
        self.LastName = LastName

   
    def get_auth_token(self):
        """
        Encode a secure token for cookie
        """
        data = [str(self.id)]
        return login_serializer.dumps(data)

    def get_id(self):
        return self.id

    @staticmethod
    def get(userid):
        result = get_user(userid)
        if not result is None:
            user = User(result[0],result[1],result[2])
            return user
        return None

    @staticmethod
    def get_unpwd(userid,pwd):
        result = get_user_pwd(userid,pwd)
        if not result is None:
            user = User(result[0],result[1],result[2])
            return user
        return None

    def __repr__(self):
        return "<User '{}'>".format(self.id)

    def __html__(self):
        return repr(self)

def hash_pass(password):
    """
    Return the md5 hash of the password+salt
    """
    salted_password = password + app.secret_key
    return md5.new(salted_password).hexdigest()

class Resource(UserMixin):
    """
    User Class for flask-Login
    """
    def __init__(self, resource_id, resource_name,primary_esf,additional_esfs,model,capabilities,latitude,longitude,cost,cost_duration ):
        self.id = resource_id
        
        self.resource_name = resource_name
        self.primary_esf = primary_esf
        self.additional_esfs = additional_esfs
        self.model = model
        self.capabilities = capabilities
        
        self.latitude = latitude
        self.longitude = longitude
        self.cost = cost
        self.cost_duration = cost_duration

   
    def get_id(self):
        return self.id
    
    def __repr__(self):
        return "<Resource '{}'>".format(self.id)

    def __html__(self):
        return repr(self)

class Incident(UserMixin):
    """
    User Class for flask-Login
    """
    def __init__(self, incident_id, date,description,latitude,longitude ):
        self.incident_id = incident_id        
        self.date = date
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
       

   
    def get_id(self):
        return self.id
    
    def __repr__(self):
        return "<Resource '{}'>".format(self.id)

    def __html__(self):
        return repr(self)

class Profile(UserMixin):
    """
    User Class for flask-Login
    """
    def __init__(self, firstname,lastname,jurisdiction,populationsize,headquarters,jobtitle,hiredate):
       
        self.firstname = firstname
        self.lastname = lastname
        self.jurisdiction = jurisdiction
        self.populationSize = populationsize
        self.headquarters = headquarters
        self.jobTitle = jobtitle
        self.hiredDate = hiredate
        
   
    def get_firstname(self):
        return self.firstname

      
    def __repr__(self):
        return "<Profile '{}'>".format(self.lastname)

    def __html__(self):
        return repr(self)

class ReportResults():
    def __init__(self, esf_id, esf_desc,resources_total,resources_in_use):
        self.esf_id = esf_id        
        self.esf_desc = esf_desc
        self.resources_total = resources_total
        self.resources_in_use = resources_in_use
        
   
    def get_id(self):
        return self.esf_id
    
    def __repr__(self):
        return "<Resource '{}'>".format(self.esf_id)

    def __html__(self):
        return repr(self)

class ResourceStatus():
    def __init__(self, resource_id, resource_name,incident,owner,start_date,return_by,action,incident_id):
        self.resource_id = resource_id        
        self.resource_name = resource_name
        self.incident = incident
        self.owner = owner
        self.start_date = start_date
        self.return_by = return_by
        self.action = action
        self.incident_id = incident_id
        
   
    def get_id(self):
        return self.resource_id
    
    def __repr__(self):
        return "<Resource '{}'>".format(self.resource_id)

    def __html__(self):
        return repr(self)

class ResourceAction():
    def __init__(self, resource_id,incident,start_date,return_by):
        self.resource_id = resource_id        
       
        self.incident = incident
       
        self.start_date = start_date
        self.return_by = return_by
        
        
   
    def get_id(self):
        return self.resource_id
    
    def __repr__(self):
        return "<Resource '{}'>".format(self.resource_id)

    def __html__(self):
        return repr(self)

class ERMSError(RuntimeError):
   def __init__(self, arg):
      self.args = arg
