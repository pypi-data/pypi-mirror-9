"""This module contains pre-defined schema that may be useful"""



#Bugsnag 
bugsnag_api_key = {"type":"string", "regex":"^[a-f1-9]{32}$"}
bugsnag_release_stage = {"type":"string"}

#Hipchat
hipchat_api_key = {"type":"string", "regex":"^[a-zA-Z1-9]{40}$"}


