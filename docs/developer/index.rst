Developer Guide
===============

Database Design
---------------

The database of the application consists of **27 tables** and the E/R diagram is given below:

   .. figure:: final-diagram.png
      :scale: 70 %
      :alt: e/r diagram

      Entity Relationship diagram of the project.

Necessary explanation about each of the tables are given in individual parts of the document.

Code
----

**Server** file has contributed by all team members and necessary explanations are made in individual sections of the report. The common parts are given below.

**Application Initialization:**

   .. code-block:: python

      def create_app():
         app.config.from_object('settings')

         app.Buglist = Buglist()
         app.Twitlist = Twitlist()
         app.Creditlist = Creditlist()
         app.messageList = MessageList()
         app.mediaList = MediaList()
         app.tagList = TagList()
         app.quizList = QuizList()

         lm.init_app(app)
         lm.login_view='login_page'

         return app

Here, we initialize global objects as application objects which are used in different functions and return the initialized application. Database connection and main function were already implemented before we contribute to the project.

**Database Initialization:**

   .. code-block:: python

      if not current_user.is_admin:
        abort(401)
      with dbapi2.connect(app.config['dsn']) as connection:
           with connection.cursor() as cursor:
                cursor.execute(open("script.sql", "r").read())
      time.sleep(5)
      return redirect(url_for('home_page'))

In database intialization function, non-admin users cannot access the related page and they will get an error message that they are not authorized to access to the page. If the user is **admin**, script file which includes createion of all tables and some initial inserts which are necessary. Since we direct the user to the home page and a query will be executed while the page is loading, we put a delay to make sure that the database intialization is completed before executing the query.

.. toctree::

   member1
   member2
   member3
   member4
   member5
