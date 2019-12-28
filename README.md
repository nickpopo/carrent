# Carrent
## Test task. Flask Application for Car Rental Company.
### TASK:
We are developing a system that provides the organization with a car rental service.

A user can rent various cars, and a car can be rented to various users.

The user has attributes email, name, language (en, ru). 

The Car has attributes name (set in two languages en, ru, 
implementation to be done taking into account possible increase in languages), 
year of creation, and date of adding a car to the system.

It is necessary to implement RestAPI with the following functionality:
- register user
- get user cars (self, admin)
- change user data (self, admin)
- get all users (admin)
For api you need to use token based authentication.
By RestApi, the name of the car must be reveived in the user's language.
 
The site should provide the following functionality:
- register user / login
- create a new car
- add a car to a user
- User information
- change user information

An unauthorized user can only access the user register / login page;
when other pages are opened, an unauthorized user should be redirected to the register user / login page.

When adding a car, email is sent to the user.

For authorization, a pair of email password is used.

For the functioning of the system, the database is filled with test data in any convenient way.

To test the operation, a test script must be written.

## Installation on Heroku
- Creating Heroku account
- Installing the Heroku CLI
- Setting Up Git
```
$ git clone https://github.com/nickpopo/carrent
$ cd carrent
```
- Creating a Heroku Application
```
$ heroku apps:create <application_name>
```
- Add Postgres addon to heroku. App working with Postgres database. You need to add Postgres SQL to your heroku.
```
$ heroku addons:add heroku-postgresql:hobby-dev
```
- Setup heroku enviroments.
```
$ heroku config:set FLASK_APP=carrent.py
```
if you want to use email notifications:
```
$ heroku config:set MAIL_SERVER=smtp.googlemail.com
$ heroku config:set MAIL_PORT=587
$ heroku config:set MAIL_USE_TLS=1
$ heroku config:set MAIL_USERNAME=<your-gmail-username>
$ heroku config:set MAIL_PASSWORD=<your-gmail-password>
```
- Deploying the Application
```
$ git push heroku master
```
If you want to create fake users and cars:
```
$ heroku run flask deploy create-users <COUNT>
$ heroku run flask deploy create-cars <COUNT>
```

done.
