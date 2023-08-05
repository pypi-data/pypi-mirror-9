# -*- coding: utf-8 -*-
# Stalker a Production Asset Management System
# Copyright (C) 2009-2014 Erkan Ozgur Yilmaz
#
# This file is part of Stalker.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


import unittest
import datetime
import logging

from stalker.db.session import DBSession
from stalker import (db, defaults, Group, Department, Project, Repository,
                     Sequence, Status, StatusList, Task, Type, User, Version,
                     Ticket, Vacation, Client)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UserTest(unittest.TestCase):
    """Tests the user class
    """

    @classmethod
    def setUpClass(cls):
        """set up the test for class
        """
        DBSession.remove()

    @classmethod
    def tearDownClass(cls):
        """clean up the test
        """
        DBSession.remove()

    def setUp(self):
        """setup the test
        """
        # setup a test database
        self.TEST_DATABASE_URI = "sqlite:///:memory:"
        db.setup()
        db.init()

        # need to have some test object for
        # a department
        self.test_department1 = Department(
            name="Test Department 1"
        )
        self.test_department2 = Department(
            name="Test Department 2"
        )
        self.test_department3 = Department(
            name="Test Department 3"
        )

        DBSession.add_all([
            self.test_department1,
            self.test_department2,
            self.test_department3
        ])

        # a couple of groups
        self.test_group1 = Group(
            name="Test Group 1"
        )
        self.test_group2 = Group(
            name="Test Group 2"
        )
        self.test_group3 = Group(
            name="Test Group 3"
        )

        DBSession.add_all([
            self.test_group1,
            self.test_group2,
            self.test_group3
        ])

        # a couple of statuses
        self.test_status1 = Status(name="Completed", code="CMPLT")
        self.test_status2 = Status(name="Work In Progress", code="WIP")
        self.test_status3 = Status(name="Waiting To Start", code="WTS")
        self.test_status4 = Status(name="Pending Review", code="PRev")

        DBSession.add_all([
            self.test_status1,
            self.test_status2,
            self.test_status3,
            self.test_status4
        ])

        # a project status list
        self.project_status_list = StatusList(
            name="Project Status List",
            statuses=[
                self.test_status1,
                self.test_status2,
                self.test_status3,
                self.test_status4
            ],
            target_entity_type=Project,
        )

        # a repository type
        self.test_repository_type = Type(
            name="Test",
            code='test',
            target_entity_type=Repository,
        )

        # a repository
        self.test_repository = Repository(
            name="Test Repository",
            type=self.test_repository_type
        )

        # a project type
        self.commercial_project_type = Type(
            name="Commercial Project",
            code='comm',
            target_entity_type=Project,
        )

        # a couple of projects
        self.test_project1 = Project(
            name="Test Project 1",
            code='tp1',
            status_list=self.project_status_list,
            type=self.commercial_project_type,
            repository=self.test_repository,
        )

        self.test_project2 = Project(
            name="Test Project 2",
            code='tp2',
            status_list=self.project_status_list,
            type=self.commercial_project_type,
            repository=self.test_repository,
        )

        self.test_project3 = Project(
            name="Test Project 3",
            code='tp3',
            status_list=self.project_status_list,
            type=self.commercial_project_type,
            repository=self.test_repository,
        )

        DBSession.add_all([
            self.test_project1,
            self.test_project2,
            self.test_project3
        ])

        # a task status list
        self.task_status_list = StatusList.query\
            .filter_by(target_entity_type='Task').first()

        self.test_lead = User(
            name='lead',
            login='lead',
            email='lead@lead.com',
            password='12345'
        )

        # a couple of tasks
        self.test_task1 = Task(
            name="Test Task 1",
            status_list=self.task_status_list,
            project=self.test_project1,
            responsible=[self.test_lead]
        )

        self.test_task2 = Task(
            name="Test Task 2",
            status_list=self.task_status_list,
            project=self.test_project1,
            responsible=[self.test_lead]
        )

        self.test_task3 = Task(
            name="Test Task 3",
            status_list=self.task_status_list,
            project=self.test_project2,
            responsible=[self.test_lead]
        )

        self.test_task4 = Task(
            name="Test Task 4",
            status_list=self.task_status_list,
            project=self.test_project3,
            responsible=[self.test_lead]
        )

        DBSession.add_all([
            self.test_task1,
            self.test_task2,
            self.test_task3,
            self.test_task4
        ])

        # for task1
        self.test_version1 = Version(
            task=self.test_task1,
            full_path='some/path'
        )
        DBSession.add(self.test_version1)

        self.test_version2 = Version(
            task=self.test_task1,
            full_path='some/path'
        )
        DBSession.add(self.test_version2)

        self.test_version3 = Version(
            task=self.test_task1,
            full_path='some/path'
        )
        DBSession.add(self.test_version3)

        # for task2
        self.test_version4 = Version(
            task=self.test_task2,
            full_path='some/path'
        )
        DBSession.add(self.test_version4)

        self.test_version5 = Version(
            task=self.test_task2,
            full_path='some/path'
        )
        DBSession.add(self.test_version5)

        self.test_version6 = Version(
            task=self.test_task2,
            full_path='some/path'
        )
        DBSession.add(self.test_version6)

        # for task3
        self.test_version7 = Version(
            task=self.test_task3,
            full_path='some/path'
        )
        DBSession.add(self.test_version7)

        self.test_version8 = Version(
            task=self.test_task3,
            full_path='some/path'
        )
        DBSession.add(self.test_version8)

        self.test_version9 = Version(
            task=self.test_task3,
            full_path='some/path'
        )
        DBSession.add(self.test_version9)

        # for task4
        self.test_version10 = Version(
            task=self.test_task4,
            full_path='some/path'
        )
        DBSession.add(self.test_version10)

        self.test_version11 = Version(
            task=self.test_task4,
            full_path='some/path'
        )
        DBSession.add(self.test_version11)

        self.test_version12 = Version(
            task=self.test_task4,
            full_path='some/path'
        )
        DBSession.add(self.test_version12)

        # *********************************************************************
        # Tickets
        # *********************************************************************

        # no need to create status list for tickets cause we have a database
        # set up an running so it will be automatically linked

        # tickets for version1
        self.test_ticket1 = Ticket(
            project=self.test_project1,
            links=[self.test_version1],
        )
        DBSession.add(self.test_ticket1)
        # set it to closed
        self.test_ticket1.resolve()

        # create a new ticket and leave it open
        self.test_ticket2 = Ticket(
            project=self.test_project1,
            links=[self.test_version1],
        )
        DBSession.add(self.test_ticket2)

        # create a new ticket and close and then reopen it
        self.test_ticket3 = Ticket(
            project=self.test_project1,
            links=[self.test_version1],
        )
        DBSession.add(self.test_ticket3)
        self.test_ticket3.resolve()
        self.test_ticket3.reopen()

        # *********************************************************************
        # tickets for version2
        # create a new ticket and leave it open
        self.test_ticket4 = Ticket(
            project=self.test_project1,
            links=[self.test_version2],
        )
        DBSession.add(self.test_ticket4)

        # create a new Ticket and close it
        self.test_ticket5 = Ticket(
            project=self.test_project1,
            links=[self.test_version2],
        )
        DBSession.add(self.test_ticket5)
        self.test_ticket5.resolve()

        # create a new Ticket and close it
        self.test_ticket6 = Ticket(
            project=self.test_project1,
            links=[self.test_version3],
        )
        DBSession.add(self.test_ticket6)
        self.test_ticket6.resolve()

        # *********************************************************************
        # tickets for version3
        # create a new ticket and close it
        self.test_ticket7 = Ticket(
            project=self.test_project1,
            links=[self.test_version3],
        )
        DBSession.add(self.test_ticket7)
        self.test_ticket7.resolve()

        # create a new ticket and close it
        self.test_ticket8 = Ticket(
            project=self.test_project1,
            links=[self.test_version3],
        )
        DBSession.add(self.test_ticket8)
        self.test_ticket8.resolve()

        # *********************************************************************
        # tickets for version4
        # create a new ticket and close it
        self.test_ticket9 = Ticket(
            project=self.test_project1,
            links=[self.test_version4],
        )
        DBSession.add(self.test_ticket9)

        self.test_ticket9.resolve()

        # no tickets for any other version
        # *********************************************************************

        # a status list for sequence
        self.sequence_status_list = StatusList.query\
            .filter_by(target_entity_type='Sequence').first()

        # a couple of sequences
        self.test_sequence1 = Sequence(
            name="Test Seq 1",
            code='ts1',
            project=self.test_project1,
            status_list=self.sequence_status_list
        )

        self.test_sequence2 = Sequence(
            name="Test Seq 2",
            code='ts2',
            project=self.test_project1,
            status_list=self.sequence_status_list
        )

        self.test_sequence3 = Sequence(
            name="Test Seq 3",
            code='ts3',
            project=self.test_project1,
            status_list=self.sequence_status_list
        )

        self.test_sequence4 = Sequence(
            name="Test Seq 4",
            code='ts4',
            project=self.test_project1,
            status_list=self.sequence_status_list
        )

        DBSession.add_all([
            self.test_sequence1,
            self.test_sequence2,
            self.test_sequence3,
            self.test_sequence4
        ])

        # a test admin
        #self.test_admin = User(
        #    name='Admin',
        #    login='admin',
        #    email='admin@admin.com',
        #    password='admin'
        #)
        self.test_admin = User.query.filter_by(name=defaults.admin_name) \
            .first()
        self.assertTrue(self.test_admin is not None)

        # create test company
        self.test_company = Client(name='Test Company')

        # create the default values for parameters
        self.kwargs = {
            'name': 'Erkan Ozgur Yilmaz',
            'login': 'eoyilmaz',
            'description': 'this is a test user',
            'password': 'hidden',
            'email': 'eoyilmaz@fake.com',
            'departments': [self.test_department1],
            'groups': [self.test_group1,
                       self.test_group2],
            'created_by': self.test_admin,
            'updated_by': self.test_admin,
            'efficiency': 1.0,
            'companies': [self.test_company]
        }

        # create a proper user object
        self.test_user = User(**self.kwargs)
        DBSession.add(self.test_user)
        DBSession.commit()

        # just change the kwargs for other tests
        self.kwargs['name'] = 'some other name'
        self.kwargs['email'] = 'some@other.email'

    def tearDown(self):
        """tear down the test
        """
        DBSession.remove()

    def test___auto_name__class_attribute_is_set_to_False(self):
        """testing if the __auto_name__ class attribute is set to False for
        User class
        """
        self.assertFalse(User.__auto_name__)

    def test_email_argument_accepting_only_string(self):
        """testing if email argument accepting only string values
        """
        # try to create a new user with wrong attribute
        test_values = [1, 1.3, ["an email"], {"an": "email"}]

        for test_value in test_values:
            self.kwargs["email"] = test_value
            self.assertRaises(TypeError, User, **self.kwargs)

    def test_email_attribute_accepting_only_string(self):
        """testing if email attribute accepting only string values
        """
        # try to assign something else than a string
        test_value = 1

        self.assertRaises(
            TypeError,
            setattr,
            self.test_user,
            "email",
            test_value
        )

        test_value = ["an email"]

        self.assertRaises(
            TypeError,
            setattr,
            self.test_user,
            "email",
            test_value
        )

    def test_email_argument_format(self):
        """testing if given an email in wrong format will raise a ValueError
        """
        test_values = [
            "an email in no format",
            "an_email_with_no_part2",
            "@an_email_with_only_part2",
            "@"
        ]

        # any of this values should raise a ValueError
        for test_value in test_values:
            self.kwargs["email"] = test_value
            self.assertRaises(ValueError, User, **self.kwargs)

    def test_email_attribute_format(self):
        """testing if given an email in wrong format will raise a ValueError
        """
        test_values = [
            "an email in no format",
            "an_email_with_no_part2",
            "@an_email_with_only_part2",
            "@",
            "eoyilmaz@",
            "eoyilmaz@some.compony@com",
        ]

        # any of these email values should raise a ValueError
        for value in test_values:
            self.assertRaises(
                ValueError,
                setattr,
                self.test_user,
                "email",
                value
            )

    def test_email_argument_should_be_a_unique_value(self):
        """testing if the email argument should be a unique value
        """
        # this test should include a database
        test_email = "test@email.com"
        self.kwargs['login'] = 'test_user1'
        self.kwargs['email'] = test_email
        user1 = User(**self.kwargs)
        DBSession.add(user1)
        DBSession.commit()

        self.kwargs['login'] = 'test_user2'
        user2 = User(**self.kwargs)
        DBSession.add(user2)

        self.assertRaises(Exception, DBSession.commit)

    def test_email_attribute_is_working_properly(self):
        """testing if email attribute works properly
        """
        test_email = "eoyilmaz@somemail.com"
        self.test_user.email = test_email
        self.assertEqual(self.test_user.email, test_email)

    def test_login_argument_conversion_to_strings(self):
        """testing if a ValueError will be raised when the given objects
        conversion to string results an empty string
        """
        test_values = ["----++==#@#$", ]
        for test_value in test_values:
            self.kwargs["login"] = test_value
            self.assertRaises(ValueError, User, **self.kwargs)

    def test_login_argument_for_empty_string(self):
        """testing if a ValueError will be raised when trying to assign an
        empty string to login argument
        """
        self.kwargs["login"] = ""
        self.assertRaises(ValueError, User, **self.kwargs)

    def test_login_attribute_for_empty_string(self):
        """testing if a ValueError will be raised when trying to assign an
        empty string to login attribute
        """
        self.assertRaises(
            ValueError,
            setattr,
            self.test_user,
            "login",
            ""
        )

    def test_login_argument_is_skipped(self):
        """testing if a TypeError will be raised when the login argument is
        skipped
        """
        self.kwargs.pop("login")
        self.assertRaises(TypeError, User, **self.kwargs)

    def test_login_argument_is_None(self):
        """testing if a TypeError will be raised when trying to assign None
        to login argument
        """
        self.kwargs["login"] = None
        self.assertRaises(TypeError, User, **self.kwargs)

    def test_login_attribute_is_None(self):
        """testing if a TypeError will be raised when trying to assign None
        to login attribute
        """
        self.assertRaises(
            TypeError,
            setattr,
            self.test_user,
            "login",
            None
        )

    def test_login_argument_formatted_correctly(self):
        """testing if login argument formatted correctly
        """
        #                 input       expected
        test_values = [
            ("e. ozgur", "eozgur"),
            ("erkan", "erkan"),
            ("Ozgur", "ozgur"),
            ("Erkan ozgur", "erkanozgur"),
            ("eRKAN", "erkan"),
            ("eRkaN", "erkan"),
            (" eRkAn", "erkan"),
            (" eRkan ozGur", "erkanozgur"),
            ("213 e.ozgur", "eozgur"),
        ]

        for valuePair in test_values:
            # set the input and expect the expected output
            self.kwargs["login"] = valuePair[0]
            test_user = User(**self.kwargs)
            self.assertEqual(
                test_user.login,
                valuePair[1]
            )

    def test_login_attribute_formatted_correctly(self):
        """testing if login attribute formatted correctly
        """
        #                 input       expected
        test_values = [
            ("e. ozgur", "eozgur"),
            ("erkan", "erkan"),
            ("Ozgur", "ozgur"),
            ("Erkan ozgur", "erkanozgur"),
            ("eRKAN", "erkan"),
            ("eRkaN", "erkan"),
            (" eRkAn", "erkan"),
            (" eRkan ozGur", "erkanozgur"),
        ]

        for valuePair in test_values:
            # set the input and expect the expected output
            self.test_user.login = valuePair[0]

            self.assertEqual(
                self.test_user.login,
                valuePair[1]
            )

    def test_login_argument_should_be_a_unique_value(self):
        """testing if the login argument should be a unique value
        """
        # this test should include a database
        test_login = 'test_user1'
        self.kwargs['login'] = test_login
        self.kwargs['email'] = "test1@email.com"
        user1 = User(**self.kwargs)
        DBSession.add(user1)
        DBSession.commit()

        self.kwargs['email'] = "test2@email.com"

        user2 = User(**self.kwargs)
        DBSession.add(user2)

        self.assertRaises(Exception, DBSession.commit)

    def test_login_argument_is_working_properly(self):
        """testing if the login argument is working properly
        """
        self.assertEqual(self.test_user.login, self.kwargs['login'])

    def test_login_attribute_is_working_properly(self):
        """testing if the login attribute is working properly
        """
        test_value = 'newlogin'
        self.test_user.login = test_value
        self.assertEqual(self.test_user.login, test_value)

    def test_last_login_attribute_None(self):
        """testing if nothing happens when the last login attribute is set to
        None
        """
        # nothing should happen
        self.test_user.last_login = None

    def test_last_login_attribute_accepts_only_datetime_instance_or_None(self):
        """testing if a TypeError will be raised for values other than
        datetime.datetime instances tried to be assigned to last_login
        attribute
        """
        test_values = [1, 2.3, "login time", ["last login time"],
                       {"a last": "login time"}]
        for test_value in test_values:
            self.assertRaises(
                TypeError,
                setattr,
                self.test_user,
                "last_login",
                test_value
            )

    def test_last_login_attribute_works_properly(self):
        """testing if the last_login attribute works properly
        """
        test_value = datetime.datetime.now()
        self.test_user.last_login = test_value
        self.assertEqual(self.test_user.last_login, test_value)

    def test_departments_argument_is_skipped(self):
        """testing if a User can be created without a Department instance
        """
        try:
            self.kwargs.pop('departments')
        except KeyError:
            pass

        new_user = User(**self.kwargs)
        self.assertEqual(new_user.departments, [])

    def test_departments_argument_is_None(self):
        """testing if a User can be created with the departments argument value
        is to None
        """
        self.kwargs['departments'] = None
        new_user = User(**self.kwargs)
        self.assertEqual(new_user.departments, [])

    def test_departments_attribute_is_set_None(self):
        """testing if a TypeError will be raised when the User's departments
        attribute set to None
        """
        self.assertRaises(TypeError, setattr, self.test_user, 'departments',
                          None)

    def test_departments_argument_is_an_empty_list(self):
        """testing if a User can be created with the departments argument is an
        empty list
        """
        self.kwargs['departments'] = []
        User(**self.kwargs)

    def test_departments_attribute_is_an_empty_list(self):
        """testing if the departments attribute can be set to an empty list
        """
        self.test_user.departments = []
        self.assertEqual(self.test_user.departments, [])

    def test_departments_argument_only_accepts_list_of_department_objects(self):
        """testing if a TypeError will be raised when trying to assign
        anything other than a Department object to departments argument
        """
        # try to assign something other than a department object
        test_values = [
            "A department",
            1,
            1.0,
            ["a department"],
            {"a": "department"}
        ]

        self.kwargs["departments"] = test_values
        self.assertRaises(TypeError, User, **self.kwargs)

    def test_departments_attribute_only_accepts_department_objects(self):
        """testing if a TypeError will be raised when trying to assign
        anything other than a Department object to departments attribute
        """
        # try to assign something other than a department
        test_value = "a department"
        self.assertRaises(
            TypeError,
            setattr,
            self.test_user,
            "departments",
            test_value
        )

    def test_departments_attribute_works_properly(self):
        """testing if departments attribute works properly
        """
        # try to set and get the same value back
        self.test_user.departments = [self.test_department2]
        self.assertEqual(
            sorted(self.test_user.departments, key=lambda x: x.name),
            sorted([self.test_department2], key=lambda x: x.name)
        )

    def test_departments_attribute_supports_appending(self):
        """testing if departments attribute supports appending
        """
        self.test_user.departments = []
        self.test_user.departments.append(self.test_department1)
        self.test_user.departments.append(self.test_department2)
        self.assertEqual(
            sorted(self.test_user.departments, key=lambda x: x.name),
            sorted([self.test_department1, self.test_department2],
                   key=lambda x: x.name)
        )

    def test_password_argument_being_None(self):
        """testing if a TypeError will be raised when trying to assign None
        to the password argument
        """
        self.kwargs["password"] = None
        self.assertRaises(TypeError, User, **self.kwargs)

    def test_password_attribute_being_None(self):
        """testing if a TypeError will be raised when tyring to assign None to
        the password attribute
        """
        self.assertRaises(
            TypeError,
            setattr,
            self.test_user,
            "password",
            None
        )

    def test_password_attribute_works_properly(self):
        """testing if password attribute works properly
        """
        test_password = "a new test password"
        self.test_user.password = test_password
        self.assertNotEquals(self.test_user.password, test_password)

    def test_password_argument_being_scrambled(self):
        """testing if password is scrambled when trying to store it
        """
        test_password = "a new test password"
        self.kwargs["password"] = test_password
        new_user = User(**self.kwargs)
        self.assertNotEquals(new_user.password, test_password)

    def test_password_attribute_being_scrambled(self):
        """testing if password is scrambled when trying to store it
        """
        test_password = "a new test password"
        self.test_user.password = test_password

        # test if they are not the same any more
        self.assertNotEquals(self.test_user.password, test_password)

    def test_check_password_works_properly(self):
        """testing if check_password method works properly
        """
        test_password = "a new test password"
        self.test_user.password = test_password

        # check if it is scrambled
        self.assertNotEquals(self.test_user.password, test_password)

        # check if check_password returns True
        self.assertTrue(self.test_user.check_password(test_password))

        # check if check_password returns False
        self.assertFalse(self.test_user.check_password("wrong pass"))

    def test_groups_argument_for_None(self):
        """testing if the groups attribute will be an empty list
        when the groups argument is None
        """
        self.kwargs["groups"] = None
        new_user = User(**self.kwargs)
        self.assertEqual(new_user.groups, [])

    def test_groups_attribute_for_None(self):
        """testing if a TypeError will be raised when groups attribute is set
        to None
        """
        self.assertRaises(TypeError, setattr, self.test_user, "groups", None)

    def test_groups_argument_accepts_only_Group_instances(self):
        """testing if a TypeError will be raised when trying to assign anything
        other then a Group instances to the group argument
        """
        test_values = [
            23123,
            1231.43122,
            "a_group",
            ["group1", "group2", 234],
        ]

        for test_value in test_values:
            self.kwargs["groups"] = test_value
            self.assertRaises(TypeError, User, **self.kwargs)

    def test_groups_attribute_accepts_only_Group_instances(self):
        """testing if a TypeError will be raised when trying to assign anything
        other then a Group instances to the group attribute
        """
        test_values = [
            23123,
            1231.43122,
            "a_group",
            ["group1", "group2", 234],
        ]

        for test_value in test_values:
            self.assertRaises(
                TypeError,
                setattr,
                self.test_user,
                "groups",
                test_value
            )

    def test_groups_attribute_works_properly(self):
        """testing if groups attribute works properly
        """
        test_pg = [self.test_group3]
        self.test_user.groups = test_pg
        self.assertEqual(self.test_user.groups, test_pg)

    def test_groups_attribute_elements_accepts_Group_only(self):
        """testing if a TypeError will be raised when trying to assign
        something other than a Group instances to the groups list
        """
        # append
        self.assertRaises(
            TypeError,
            self.test_user.groups.append,
            0
        )

        # __setitem__
        self.assertRaises(
            TypeError,
            self.test_user.groups.__setitem__,
            0,
            0
        )

    def test_projects_attribute_is_None(self):
        """testing if a TypeError will be raised when the projects attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_user, 'projects', None)

    def test_projects_attribute_is_set_to_a_value_which_is_not_a_list(self):
        """testing if the projects attribute is accepting lists only
        """
        self.assertRaises(TypeError, setattr, self.test_user, 'projects',
                          'not a list')

    def test_projects_attribute_is_set_to_list_of_other_objects_than_Project_instances(self):
        """testing if a TypeError will be raised when the projects attribute is
        set to a value which is a list of other values than Projects instances
        """
        self.assertRaises(TypeError, setattr, self.test_user, 'projects',
                          ['not', 'a', 'list', 'of', 'projects', 32])

    def test_projects_attribute_is_working_properly(self):
        """testing if the projects attribute is working properly
        """
        test_list = [self.test_project1, self.test_project2]
        self.test_user.projects = test_list
        self.assertEqual(
            sorted(test_list, key=lambda x: x.name),
            sorted(self.test_user.projects, key=lambda x: x.name)
        )
        self.test_user.projects.append(self.test_project3)
        self.assertTrue(self.test_project3 in self.test_user.projects)
        # also check the backref
        self.assertTrue(self.test_user in self.test_project1.users)
        self.assertTrue(self.test_user in self.test_project2.users)
        self.assertTrue(self.test_user in self.test_project3.users)

    def test_tasks_attribute_None(self):
        """testing if a TypeError will be raised when the tasks attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_user, "tasks", None)

    def test_tasks_attribute_accepts_only_list_of_task_objects(self):
        """testing if a TypeError will be raised when trying to assign
        anything other than a list of task objects to the tasks argument
        """
        test_values = [12312, 1233244.2341, ["aTask1", "aTask2"], "a_task"]

        for test_value in test_values:
            self.assertRaises(
                TypeError,
                setattr,
                self.test_user,
                "tasks",
                test_value
            )

    def test_tasks_attribute_accepts_an_empty_list(self):
        """testing if nothing happens when trying to assign an empty list to
        tasks attribute
        """
        # this should work without any error
        self.test_user.tasks = []

    def test_tasks_attribute_works_properly(self):
        """testing if tasks attribute is working properly
        """
        tasks = [self.test_task1,
                 self.test_task2,
                 self.test_task3,
                 self.test_task4]

        self.test_user.tasks = tasks

        self.assertEqual(self.test_user.tasks, tasks)

    def test_tasks_attribute_elements_accepts_Tasks_only(self):
        """testing if a TypeError will be raised when trying to assign
        something other than a Task object to the tasks list
        """
        # append
        self.assertRaises(
            TypeError,
            self.test_user.tasks.append,
            0
        )

    def test_equality_operator(self):
        """testing equality of two users
        """
        self.kwargs.update({
            "name": "Generic User",
            "description": "this is a different user",
            "login": "guser",
            "email": "generic.user@generic.com",
            "password": "verysecret",
        })

        new_user = User(**self.kwargs)

        self.assertFalse(self.test_user == new_user)

    def test_inequality_operator(self):
        """testing inequality of two users
        """
        self.kwargs.update({
            "name": "Generic User",
            "description": "this is a different user",
            "login": "guser",
            "email": "generic.user@generic.com",
            "password": "verysecret",
        })

        new_user = User(**self.kwargs)

        self.assertTrue(self.test_user != new_user)

    def test___repr__(self):
        """testing the representation
        """
        self.assertEqual(
            self.test_user.__repr__(),
            "<%s ('%s') (User)>" % (
                self.test_user.name,
                self.test_user.login)
        )

    def test_tickets_attribute_is_an_empty_list_by_default(self):
        """testing if the User.tickets is an empty list by default
        """
        self.assertEqual(self.test_user.tickets, [])

    def test_open_tickets_attribute_is_an_empty_list_by_default(self):
        """testing if the User.open_tickets is an empty list by default
        """
        self.assertEqual(self.test_user.open_tickets, [])

    def test_tickets_attribute_is_read_only(self):
        """testing if the User.tickets attribute is a read only attribute
        """
        self.assertRaises(
            AttributeError, setattr, self.test_user, 'tickets', []
        )

    def test_open_tickets_attribute_is_read_only(self):
        """testing if the User.open_tickets attribute is a read only attribute
        """
        self.assertRaises(AttributeError, setattr, self.test_user,
                          'open_tickets', [])

    def test_tickets_attribute_returns_all_tickets_owned_by_this_user(self):
        """testing if User.tickets returns all the tickets owned by this user
        """
        self.assertEqual(len(self.test_user.tasks), 0)

        # there should be no tickets assigned to this user
        self.assertTrue(self.test_user.tickets == [])

        # be careful not all of these are open tickets
        self.test_ticket1.reassign(self.test_user, self.test_user)
        self.test_ticket2.reassign(self.test_user, self.test_user)
        self.test_ticket3.reassign(self.test_user, self.test_user)
        self.test_ticket4.reassign(self.test_user, self.test_user)
        self.test_ticket5.reassign(self.test_user, self.test_user)
        self.test_ticket6.reassign(self.test_user, self.test_user)
        self.test_ticket7.reassign(self.test_user, self.test_user)
        self.test_ticket8.reassign(self.test_user, self.test_user)

        # now we should have some tickets
        self.assertTrue(len(self.test_user.tickets) > 0)

        # now check for exact items
        self.assertEqual(
            sorted(self.test_user.tickets, key=lambda x: x.name),
            sorted([self.test_ticket2, self.test_ticket3, self.test_ticket4],
                   key=lambda x: x.name)
        )

    def test_open_tickets_attribute_returns_all_open_tickets_owned_by_this_user(self):
        """testing if User.open_tickets returns all the open tickets owned by
        this user
        """
        self.assertEqual(len(self.test_user.tasks), 0)

        # there should be no tickets assigned to this user
        self.assertTrue(self.test_user.open_tickets == [])

        # assign the user to some tickets
        self.test_ticket1.reopen(self.test_user)
        self.test_ticket2.reopen(self.test_user)
        self.test_ticket3.reopen(self.test_user)
        self.test_ticket4.reopen(self.test_user)
        self.test_ticket5.reopen(self.test_user)
        self.test_ticket6.reopen(self.test_user)
        self.test_ticket7.reopen(self.test_user)
        self.test_ticket8.reopen(self.test_user)

        # be careful not all of these are open tickets
        self.test_ticket1.reassign(self.test_user, self.test_user)
        self.test_ticket2.reassign(self.test_user, self.test_user)
        self.test_ticket3.reassign(self.test_user, self.test_user)
        self.test_ticket4.reassign(self.test_user, self.test_user)
        self.test_ticket5.reassign(self.test_user, self.test_user)
        self.test_ticket6.reassign(self.test_user, self.test_user)
        self.test_ticket7.reassign(self.test_user, self.test_user)
        self.test_ticket8.reassign(self.test_user, self.test_user)

        # now we should have some open tickets
        self.assertTrue(len(self.test_user.open_tickets) > 0)

        # now check for exact items
        self.assertEqual(
            sorted(self.test_user.open_tickets, key=lambda x: x.name),
            sorted([
                self.test_ticket1,
                self.test_ticket2,
                self.test_ticket3,
                self.test_ticket4,
                self.test_ticket5,
                self.test_ticket6,
                self.test_ticket7,
                self.test_ticket8,
            ], key=lambda x: x.name)
        )

        # close a couple of them
        from stalker.models.ticket import FIXED, CANTFIX, INVALID

        self.test_ticket1.resolve(self.test_user, FIXED)
        self.test_ticket2.resolve(self.test_user, INVALID)
        self.test_ticket3.resolve(self.test_user, CANTFIX)

        # new check again
        self.assertEqual(
            sorted(self.test_user.open_tickets, key=lambda x: x.name),
            sorted([
                self.test_ticket4,
                self.test_ticket5,
                self.test_ticket6,
                self.test_ticket7,
                self.test_ticket8
            ], key=lambda x: x.name)
        )

    def test_tjp_id_is_working_properly(self):
        """testing if the tjp_id is working properly
        """
        self.assertEqual(self.test_user.tjp_id, 'User_%s' % self.test_user.id)

    def test_to_tjp_is_working_properly(self):
        """testing if the to_tjp property is working properly
        """
        expected_tjp = \
            'resource User_%s "User_%s" {\n    efficiency 1.0\n}' % \
            (self.test_user.id, self.test_user.id)

        self.assertEqual(expected_tjp, self.test_user.to_tjp)

    def test_to_tjp_is_working_properly_for_a_user_with_vacations(self):
        """testing if the to_tjp property is working properly for a user with
        vacations
        """
        personal_vacation = Type(
            name='Personal',
            code='PERS',
            target_entity_type='Vacation'
        )

        Vacation(
            user=self.test_user,
            type=personal_vacation,
            start=datetime.datetime(2013, 6, 7, 0, 0),
            end=datetime.datetime(2013, 6, 21, 0, 0)
        )

        Vacation(
            user=self.test_user,
            type=personal_vacation,
            start=datetime.datetime(2013, 7, 1, 0, 0),
            end=datetime.datetime(2013, 7, 15, 0, 0)
        )

        expected_tjp = """resource User_%s "User_%s" {
    efficiency 1.0
    vacation 2013-06-07-00:00:00 - 2013-06-21-00:00:00
    vacation 2013-07-01-00:00:00 - 2013-07-15-00:00:00
}""" % (self.test_user.id, self.test_user.id)

        # print expected_tjp
        # print '---------------'
        # print self.test_user.to_tjp

        self.assertEqual(
            expected_tjp,
            self.test_user.to_tjp
        )

    def test_vacations_attribute_is_set_to_None(self):
        """testing if a TypeError will be raised when the vacations attribute
        is set to None
        """
        self.assertRaises(TypeError, setattr, self.test_user, 'vacations',
                          None)

    def test_vacations_attribute_is_not_a_list(self):
        """testing if a TypeError will be raised when the vacations attribute
        is set to a value other than a list
        """
        self.assertRaises(TypeError, setattr, self.test_user, 'vacations',
                          'not a list of Vacation instances')

    def test_vacations_attribute_is_not_a_list_of_Vacation_instances(self):
        """testing if a TypeError will be raised when the vacations attribute
        is set to a list of other objects than Vacation instances
        """
        self.assertRaises(TypeError, setattr, self.test_user, 'vacations',
                          ['list of', 'other', 'instances', 1])

    def test_vacations_attribute_is_working_properly(self):
        """testing if the vacations attribute is working properly
        """
        some_other_user = User(
            name='Some Other User',
            login='sou',
            email='some@other.user.com',
            password='my password'
        )

        personal_vac_type = Type(
            name='Personal Vacation',
            code='PERS',
            target_entity_type='Vacation'
        )

        vac1 = Vacation(
            user=some_other_user,
            type=personal_vac_type,
            start=datetime.datetime(2013, 6, 7),
            end=datetime.datetime(2013, 6, 10)
        )

        self.assertFalse(
            vac1 in self.test_user.vacations
        )

        self.test_user.vacations.append(vac1)

        self.assertTrue(
            vac1 in self.test_user.vacations
        )

    def test_efficiency_argument_skipped(self):
        """testing if the efficiency attribute value will be 1.0 if the
        efficiency argument is skipped
        """
        self.kwargs.pop('efficiency')
        new_user = User(**self.kwargs)
        self.assertEqual(1.0, new_user.efficiency)

    def test_efficiency_argument_is_None(self):
        """testing if the efficiency attribute value will be 1.0 if the
        efficiency argument is None
        """
        self.kwargs['efficiency'] = None
        new_user = User(**self.kwargs)
        self.assertEqual(1.0, new_user.efficiency)

    def test_efficiency_attribute_is_set_to_None(self):
        """testing if the efficiency attribute value will be 1.0 if it is set
        to None
        """
        self.test_user.efficiency = 4.0
        self.test_user.efficiency = None
        self.assertEqual(1.0, self.test_user.efficiency)

    def test_efficiency_argument_is_not_a_float_or_integer(self):
        """testing if a TypeError will be raised when the efficiency argument
        is not a float or integer
        """
        self.kwargs['efficiency'] = 'not a float or integer'
        with self.assertRaises(TypeError) as cm:
            User(**self.kwargs)

        self.assertEqual(
            'User.efficiency should be a float number greater or equal to '
            '0.0, not str',
            str(cm.exception)
        )

    def test_efficiency_attribute_is_not_a_float_or_integer(self):
        """testing if a TypeError will be raised when the efficiency attribute
        is set to a value other than a float or integer
        """
        with self.assertRaises(TypeError) as cm:
            self.test_user.efficiency = 'not a float or integer'

        self.assertEqual(
            'User.efficiency should be a float number greater or equal to '
            '0.0, not str',
            str(cm.exception)
        )

    def test_efficiency_argument_is_a_negative_float_or_integer(self):
        """testing if a ValueError will be raised when the efficiency argument
        is a negative float or integer
        """
        self.kwargs['efficiency'] = -1
        with self.assertRaises(ValueError) as cm:
            User(**self.kwargs)

        self.assertEqual(
            'User.efficiency should be a float number greater or equal to '
            '0.0, not -1',
            str(cm.exception)
        )

    def test_efficiency_attribute_is_a_negative_float_or_integer(self):
        """testing if a ValueError will be raised when the efficiency attribute
        is set to a negative float or integer
        """
        with self.assertRaises(ValueError) as cm:
            self.test_user.efficiency = -2.0

        self.assertEqual(
            'User.efficiency should be a float number greater or equal to '
            '0.0, not -2.0',
            str(cm.exception)
        )

    def test_efficiency_argument_is_working_properly(self):
        """testing if the efficiency argument value is correctly passed to the
        efficiency attribute
        """
        # integer value
        self.kwargs['efficiency'] = 2
        new_user = User(**self.kwargs)
        self.assertEqual(
            2.0,
            new_user.efficiency
        )

        # float value
        self.kwargs['efficiency'] = 2.3
        new_user = User(**self.kwargs)
        self.assertEqual(
            2.3,
            new_user.efficiency
        )

    def test_efficiency_attribute_is_working_properly(self):
        """testing if the efficiency attribute value can correctly be changed
        """
        # integer
        self.assertNotEqual(
            2,
            self.test_user.efficiency
        )

        self.test_user.efficiency = 2
        self.assertEqual(
            2.0,
            self.test_user.efficiency
        )

        # float
        self.assertNotEqual(
            2.3,
            self.test_user.efficiency
        )

        self.test_user.efficiency = 2.3
        self.assertEqual(
            2.3,
            self.test_user.efficiency
        )

    def test_companies_argument_is_skipped(self):
        """testing if the companies attribute will be set to an empty list when
        the company argument is skipped
        """
        self.kwargs.pop('companies')
        new_user = User(**self.kwargs)
        self.assertEquals(new_user.companies, [])

    def test_companies_argument_is_None(self):
        """testing if the companies argument is set to None the companies
        attribute will be an empty list
        """
        self.kwargs['companies'] = None
        new_user = User(**self.kwargs)
        self.assertTrue(new_user.companies == [])

    def test_companies_attribute_is_set_to_None(self):
        """testing if a the companies attribute will be an empty list if it is
        set to None
        """
        self.assertTrue(self.test_user.companies is not None)
        with self.assertRaises(TypeError) as cm:
            self.test_user.companies = None
        self.assertEqual(
            str(cm.exception),
            "'NoneType' object is not iterable"
        )

    def test_companies_argument_is_not_a_list(self):
        """testing if a TypeError will be raised if the companies argument is
        not a list
        """
        self.kwargs['companies'] = 'not a list of clients'
        with self.assertRaises(TypeError) as cm:
            User(**self.kwargs)

        self.assertEqual(
            str(cm.exception),
            'ClientUser.client should be instance of '
            'stalker.models.client.Client, not str'
        )

    def test_companies_argument_is_not_a_list_of_client_instances(self):
        """testing if a TypeError will be raised when the companies argument is
        not a list of Client instances
        """
        test_value = [1, 1.2, "a user", ["a", "user"], {"a": "user"}]
        self.kwargs["companies"] = test_value
        self.assertRaises(
            TypeError,
            User,
            **self.kwargs
        )

    def test_companies_attribute_is_set_to_a_value_other_than_a_list_of_client_instances(self):
        """testing if a TypeError will be raised when the companies attribute
        is set to a value other than a list of Client instances
        """
        test_value = [1, 1.2, "a user", ["a", "user"], {"a": "user"}]
        with self.assertRaises(TypeError) as cm:
            self.test_user.companies = test_value

        self.assertEqual(
            str(cm.exception),
            'ClientUser.client should be instance of '
            'stalker.models.client.Client, not int'
        )

    def test_watching_attribute_is_a_list_of_other_values_than_Task(self):
        """testing if a TypeError will be raised when the watching attribute is
        set to a list of other values than a Task
        """
        with self.assertRaises(TypeError) as cm:
            self.test_user.watching = ['not', 1, 'list of tasks']

        self.assertEqual(
            str(cm.exception),
            'Any element in User.watching should be an instance of '
            'stalker.models.task.Task not str'
        )

    def test_watching_attribute_is_working_properly(self):
        """testing if the watching attribute is working properly
        """
        test_value = [self.test_task1, self.test_task2]
        self.assertEqual(self.test_user.watching, [])
        self.test_user.watching = test_value
        self.assertEqual(
            sorted(test_value, key=lambda x: x.name),
            sorted(self.test_user.watching, key=lambda x: x.name)
        )

    # def test_hash_value(self):
    #     """testing if the hash value is correctly calculated
    #     """
    #     self.assertEqual(
    #         hash(self.test_user),
    #         hash(self.test_user.id) +
    #         2 * hash(self.test_user.name) +
    #         3 * hash(self.test_user.entity_type)
    #     )

    def test_rate_argument_is_skipped(self):
        """testing if the rate attribute will be 0 when the rate argument is
        skipped
        """
        if 'rate' in self.kwargs:
            self.kwargs.pop('rate')

        new_user = User(**self.kwargs)
        self.assertEqual(new_user.rate, 0)

    def test_rate_argument_is_none(self):
        """testing if the rate attribute will be 0 when the rate argument is
        None
        """
        self.kwargs['rate'] = None
        new_user = User(**self.kwargs)
        self.assertEqual(new_user.rate, 0)

    def test_rate_attribute_is_set_to_none(self):
        """testing if the rate will be set to 0 if it is set to None
        """
        self.assertNotEqual(self.test_user.rate, None)

        self.test_user.rate = None
        self.assertEqual(self.test_user.rate, 0)

    def test_rate_argument_is_not_a_float_or_integer_value(self):
        """testing if a TypeError will be raised when the rate argument is not
        an integer or float value
        """
        self.kwargs['rate'] = 'some string'
        with self.assertRaises(TypeError) as cm:
            User(**self.kwargs)

        self.assertEqual(
            str(cm.exception),
            'User.rate should be a float number greater or equal to 0.0, not '
            'str'
        )

    def test_rate_attribute_is_not_a_float_or_integer_value(self):
        """testing if a TypeError will be raised when the rate attribute is set
        to a value other than an integer or float
        """
        with self.assertRaises(TypeError) as cm:
            self.test_user.rate = 'some string'

        self.assertEqual(
            str(cm.exception),
            'User.rate should be a float number greater or equal to 0.0, not '
            'str'
        )

    def test_rate_argument_is_a_negative_number(self):
        """testing if a ValueError will be raised when the rate argument is a
        negative value
        """
        self.kwargs['rate'] = -1
        with self.assertRaises(ValueError) as cm:
            User(**self.kwargs)

        self.assertEqual(
            str(cm.exception),
            'User.rate should be a float number greater or equal to 0.0, not '
            '-1'
        )

    def test_rate_attribute_is_set_to_a_negative_number(self):
        """testing if a ValueError will be raised when the rate attribute is
        set to a negative number
        """
        with self.assertRaises(ValueError) as cm:
            self.test_user.rate = -1

        self.assertEqual(
            str(cm.exception),
            'User.rate should be a float number greater or equal to 0.0, not '
            '-1'
        )

    def test_rate_argument_is_working_properly(self):
        """testing if the rate argument is working properly
        """
        test_value = 102.3
        self.kwargs['rate'] = test_value
        new_user = User(**self.kwargs)
        self.assertEqual(new_user.rate, test_value)

    def test_rate_attribute_is_working_properly(self):
        """testing if rate attribute is working properly
        """
        test_value = 212.5
        self.assertNotEqual(self.test_user.rate, test_value)
        self.test_user.rate = test_value
        self.assertEqual(self.test_user.rate, test_value)
