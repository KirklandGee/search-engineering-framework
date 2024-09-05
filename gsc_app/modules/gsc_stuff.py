import gscwrapper
#authentificate 
account = gscwrapper.generate_auth(
    '.token_cache', 
    serialize='.token_cache'
)
#we choose the website we want 
webproperty = account['sc-domain:perfectextraction.com']
report = (
    webproperty
    #we call the query method 
    .query
    #we define the dates 
    .range(start="2023-01-01", stop="2023-02-01")
    #we define the dimensions 
    .dimensions(['page'])
    #we get the data 
    .get()
)