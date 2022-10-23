db = db.getSiblingDB('gutendexer')

db.createCollection('reviews');

db.createUser({
  user: 'api',
  pwd: 'apiPassword',
  roles: [
    'readWrite'  
  ],
});
