# Unofficial Udacity API (for Python)

**by Ty-Lucas Kelley**

![build-status](https://travis-ci.org/tylucaskelley/udacity-api-python.svg?branch=master)
![version](https://pypip.in/version/udacity/badge.svg)
![downloads](https://pypip.in/download/udacity/badge.svg)

---

    ##  ##   #####     ####     #####   ######   ######   ##  ##
    ##  ##   ##   #   ##  ##   ##         ##       ##     ##  ##
    ##  ##   ##   #   ######   ##         ##       ##      ####
    ##  ##   ##   #   ##  ##   ##         ##       ##       ##
     ####    #####    ##  ##    #####   ######     ##       ##

This is an unofficial client library for interacting with Udacity courses and users.
It is made up of two parts:

* [Catalog](#catalog)
    * A wrapper for Udacity's public [Catalog API](http://udacity.com/public-api/v0/courses)
* [User](#user)
    * Log into your Udacity account, see user info, and check course progress

### Warning

Note that this is not an official Udacity product. They are allowed to change their internal
API at any time, and I will try my best to make sure this library gets updated as well.

In the end, be sure to use this only for personal purposes, not any serious application with
a lot of users.

### Installation

It's on pip! Install it from the terminal, with Python 2 or 3:

    $ pip install udacity

You can then include it in your application:

    import udacity

### User

The `User` class is used to view a user's account info and see their progress in courses.
It includes a lot of convenience functions.

Run `pydoc udacity.User` for information about each method and what it returns.

Example usage:

```py
import udacity

user = udacity.User('email@example.com', 'password123')
name = user.name()

# print out quiz completion rate in each course
for course in user.enrollments():
    prog = user.progress(course)
    print('Course: ' + prog['title'])
    print('\t' + str(prog['quizzes_completed']) + '/'
            + str(prog['quiz_count']) + ' quizzes completed')
```

### Catalog

The `Catalog` class can be used to filter data from Udacity's Catalog API. It has
plenty of convenience functions.

Run `pydoc udacity.Catalog` for information about each method and what it returns.

Example usage:

```py
import udacity

c = udacity.Catalog()

tracks = c.tracks()

track_names = [t['name'] for t in tracks]
web_dev_teachers = c.instructors('cs253')
nd001_description = c.degree('nd001')['expected_learning']
```
