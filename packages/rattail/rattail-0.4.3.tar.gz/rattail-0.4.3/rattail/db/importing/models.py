# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Model Importers
"""

from __future__ import unicode_literals

import logging

from sqlalchemy.orm import joinedload, joinedload_all

from rattail.db import model
from rattail.db.api import set_regular_price, set_current_sale_price
from rattail.db.auth import administrator_role

from .core import Importer


log = logging.getLogger(__name__)


class PersonImporter(Importer):
    """
    Person data importer.
    """
    model_class = model.Person
    supported_fields = [
        'uuid',
        'first_name',
        'last_name',
        'display_name',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'first_name', 'last_name', 'display_name')


class PersonEmailAddressImporter(Importer):
    """
    Person email address data importer.
    """
    model_class = model.PersonEmailAddress
    supported_fields = [
        'uuid',
        'parent_uuid',
        'type',
        'address',
        'preference',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'address')


class PersonPhoneNumberImporter(Importer):
    """
    Person phone number data importer.
    """
    model_class = model.PersonPhoneNumber
    supported_fields = [
        'uuid',
        'parent_uuid',
        'type',
        'number',
        'preference',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'number')


class UserImporter(Importer):
    """
    User data importer.
    """
    model_class = model.User
    simple_fields = [
        'uuid',
        'username',
        'password',
        'salt',
        'person_uuid',
        'active',
        ]
    supported_fields = simple_fields + [
        'admin',
        ]

    def setup(self, progress):
        self.admin = administrator_role(self.session)

    def normalize_record(self, data):
        self.string_or_null(data, 'username')

    def normalize_instance(self, user):
        return {
            'uuid': user.uuid,
            'username': user.username,
            'password': user.password,
            'salt': user.salt,
            'person_uuid': user.person_uuid,
            'active': user.active,
            'admin': self.admin in user.roles,
            }

    def update_instance(self, user, data):
        super(UserImporter, self).update_instance(user, data)
        if 'admin' in data:
            if data['admin']:
                if self.admin not in user.roles:
                    user.roles.append(self.admin)
            else:
                if self.admin in user.roles:
                    user.roles.remove(self.admin)


class StoreImporter(Importer):
    """
    Store data importer.
    """
    model_class = model.Store
    simple_fields = [
        'uuid',
        'id',
        'name',
        ]
    supported_fields = simple_fields + [
        'phone_number',
        'fax_number',
        ]

    def cache_query_options(self):
        if 'phone_number' in self.fields or 'fax_number' in self.fields:
            return [joinedload(model.Store.phones)]

    def normalize_record(self, data):
        self.string_or_null(data, 'name', 'phone_number', 'fax_number')

    def normalize_instance(self, store):
        data = super(StoreImporter, self).normalize_instance(store)

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in store.phones:
                if phone.type == 'Voice':
                    data['phone_number'] = phone.number
                    break

        if 'fax_number' in self.fields:
            data['fax_number'] = None
            for phone in store.phones:
                if phone.type == 'Fax':
                    data['fax_number'] = phone.number
                    break

        return data

    def update_instance(self, store, data):
        super(StoreImporter, self).update_instance(store, data)

        if 'phone_number' in data:
            number = data['phone_number'] or None
            if number:
                found = False
                for phone in store.phones:
                    if phone.type == 'Voice':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    store.add_phone_number(number, type='Voice')
            else:
                for phone in list(store.phones):
                    if phone.type == 'Voice':
                        store.phones.remove(phone)

        if 'fax_number' in data:
            number = data['fax_number'] or None
            if number:
                found = False
                for phone in store.phones:
                    if phone.type == 'Fax':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    store.add_phone_number(number, type='Fax')
            else:
                for phone in list(store.phones):
                    if phone.type == 'Fax':
                        store.phones.remove(phone)


class EmployeeImporter(Importer):
    """
    Employee data importer.
    """
    model_class = model.Employee
    simple_fields = [
        'uuid',
        'id',
        'person_uuid',
        'display_name',
        'status',
        ]
    supported_fields = simple_fields + [
        'customer_id',
        'first_name',
        'last_name',
        'phone_number',
        'phone_number_2',
        'email_address',
        ]

    def setup(self, progress=None):
        if 'customer_id' in self.fields:
            self.customers = self.cache_model(model.Customer, 'id')

    def cache_query_options(self):
        options = []
        if 'first_name' in self.fields or 'last_name' in self.fields:
            options.append(joinedload(model.Employee.person))
        if 'phone_number' in self.fields or 'phone_number_2' in self.fields:
            options.append(joinedload(model.Employee.phones))
        if 'email_address' in self.fields:
            options.append(joinedload(model.Employee.email))
        return options

    def normalize_record(self, data):
        self.string_or_null(data, 'display_name', 'first_name', 'last_name', 'customer_id',
                            'phone_number', 'phone_number_2', 'email_address')
        self.int_or_null(data, 'id', 'status')
        self.prioritize_2(data, 'phone_number')

    def normalize_instance(self, employee):
        data = super(EmployeeImporter, self).normalize_instance(employee)

        if 'customer_id' in self.fields:
            customer = employee.person.customers[0] if employee.person.customers else None
            data['customer_id'] = customer.id if customer else None

        if 'first_name' in self.fields:
            data['first_name'] = employee.first_name
        if 'last_name' in self.fields:
            data['last_name'] = employee.last_name

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in employee.phones:
                if phone.type == 'Home':
                    data['phone_number'] = phone.number
                    break

        if 'phone_number_2' in self.fields:
            data['phone_number_2'] = None
            first = False
            for phone in employee.phones:
                if phone.type == 'Home':
                    if first:
                        data['phone_number_2'] = phone.number
                        break
                    first = True

        if 'email_address' in self.fields:
            email = employee.email
            data['email_address'] = email.address if email else None

        return data

    def update_instance(self, employee, data):
        super(EmployeeImporter, self).update_instance(employee, data)

        if 'first_name' in data:
            employee.first_name = data['first_name']
        if 'last_name' in data:
            employee.last_name = data['last_name']

        if 'customer_id' in data:
            id_ = data['customer_id']
            if id_:
                customer = self.customers.get(id_)
                if not customer:
                    customer = model.Customer()
                    customer.id = id_
                    customer.name = employee.display_name
                    self.session.add(customer)
                    self.customers[customer.id] = customer
                if employee.person not in customer.people:
                    customer.people.append(employee.person)
            else:
                for customer in list(employee.person.customers):
                    if len(customer.people) > 1:
                        if employee.person in customer.people:
                            customer.people.remove(employee.person)

        if 'phone_number' in data:
            number = data['phone_number']
            if number:
                found = False
                for phone in employee.phones:
                    if phone.type == 'Home':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    employee.add_phone_number(number, type='Home')
            else:
                for phone in list(employee.phones):
                    if phone.type == 'Home':
                        employee.phones.remove(phone)

        if 'phone_number_2' in data:
            number = data['phone_number_2']
            if number:
                found = False
                first = False
                for phone in employee.phones:
                    if phone.type == 'Home':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    employee.add_phone_number(number, type='Home')
            else:
                first = False
                for phone in list(employee.phones):
                    if phone.type == 'Home':
                        if first:
                            employee.phones.remove(phone)
                            break
                        first = True

        if 'email_address' in data:
            address = data['email_address']
            if address:
                if employee.email:
                    if employee.email.address != address:
                        employee.email.address = address
                else:
                    employee.add_email_address(address)
            else:
                if len(employee.emails):
                    del employee.emails[:]


class CustomerGroupImporter(Importer):
    """
    CustomerGroup data importer.
    """
    model_class = model.CustomerGroup
    supported_fields = [
        'uuid',
        'id',
        'name',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'name')


class CustomerImporter(Importer):
    """
    Customer data importer.
    """
    model_class = model.Customer
    simple_fields = [
        'uuid',
        'id',
        'name',
        'email_preference',
        ]
    supported_fields = simple_fields + [
        'first_name',
        'last_name',
        'phone_number',
        'phone_number_2',
        'email_address',
        'group_id',
        'group_id_2',
        ]

    def setup(self, progress=None):
        if 'group_id' in self.fields or 'group_id_2' in self.fields:
            self.groups = self.cache_model(model.CustomerGroup, 'id')

    def cache_query_options(self):
        options = []
        if 'first_name' in self.fields or 'last_name' in self.fields:
            options.append(joinedload(model.Customer._person))
        if 'phone_number' in self.fields or 'phone_number_2' in self.fields:
            options.append(joinedload(model.Customer.phones))
        if 'email_address' in self.fields:
            options.append(joinedload(model.Customer.email))
        if 'group_id' in self.fields or 'group_id_2' in self.fields:
            options.append(joinedload_all(model.Customer._groups, model.CustomerGroupAssignment.group))
        return options

    def normalize_record(self, data):
        self.string_or_null(data, 'id', 'name', 'first_name', 'last_name',
                            'phone_number', 'phone_number_2', 'email_address',
                            'group_id', 'group_id_2')
        self.prioritize_2(data, 'phone_number')
        self.prioritize_2(data, 'group_id')

    def normalize_instance(self, customer):
        data = super(CustomerImporter, self).normalize_instance(customer)
        if 'first_name' in self.fields or 'last_name' in self.fields:
            person = customer.person
            if person:
                if 'first_name' in self.fields:
                    data['first_name'] = person.first_name
                if 'last_name' in self.fields:
                    data['last_name'] = person.last_name
            else:
                if 'first_name' in self.fields:
                    data['first_name'] = None
                if 'last_name' in self.fields:
                    data['last_name'] = None

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in customer.phones:
                if phone.type == 'Voice':
                    data['phone_number'] = phone.number
                    break

        if 'phone_number_2' in self.fields:
            data['phone_number_2'] = None
            first = False
            for phone in customer.phones:
                if phone.type == 'Voice':
                    if first:
                        data['phone_number_2'] = phone.number
                        break
                    first = True

        if 'email_address' in self.fields:
            email = customer.email
            data['email_address'] = email.address if email else None

        if 'group_id' in self.fields:
            group = customer.groups[0] if customer.groups else None
            data['group_id'] = group.id if group else None

        if 'group_id_2' in self.fields:
            group = customer.groups[1] if customer.groups and len(customer.groups) > 1 else None
            data['group_id_2'] = group.id if group else None

        return data

    def update_instance(self, customer, data):
        super(CustomerImporter, self).update_instance(customer, data)
        if 'first_name' in data or 'last_name' in data:
            person = customer.person
            if not person:
                person = model.Person()
                customer.people.append(person)
        if 'first_name' in data:
            person.first_name = data['first_name']
        if 'last_name' in data:
            person.last_name = data['last_name']

        if 'phone_number' in data:
            number = data['phone_number']
            if number:
                found = False
                for phone in customer.phones:
                    if phone.type == 'Voice':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    customer.add_phone_number(number, type='Voice')
            else:
                for phone in list(customer.phones):
                    if phone.type == 'Voice':
                        customer.phones.remove(phone)

        if 'phone_number_2' in data:
            number = data['phone_number_2']
            if number:
                found = False
                first = False
                for phone in customer.phones:
                    if phone.type == 'Voice':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    customer.add_phone_number(number, type='Voice')
            else:
                first = False
                for phone in list(customer.phones):
                    if phone.type == 'Voice':
                        if first:
                            customer.phones.remove(phone)
                            break
                        first = True

        if 'email_address' in data:
            address = data['email_address']
            if address:
                if customer.email:
                    if customer.email.address != address:
                        customer.email.address = address
                else:
                    customer.add_email_address(address)
            else:
                if len(customer.emails):
                    del customer.emails[:]

        if 'group_id' in data:
            id_ = data['group_id']
            if id_:
                group = self.groups.get(id_)
                if not group:
                    group = model.CustomerGroup()
                    group.id = id_
                    group.name = "(auto-created)"
                    self.session.add(group)
                    self.groups[group.id] = group
                if group in customer.groups:
                    if group is not customer.groups[0]:
                        customer.groups.remove(group)
                        customer.groups.insert(0, group)
                else:
                    customer.groups.insert(0, group)
            else:
                if customer.groups:
                    del customer.groups[:]

        if 'group_id_2' in data:
            id_ = data['group_id_2']
            if id_:
                group = self.groups.get(id_)
                if not group:
                    group = model.CustomerGroup()
                    group.id_ = id_
                    group.name = "(auto-created)"
                    self.session.add(group)
                    self.groups[group.id] = group
                if group in customer.groups:
                    if len(customer.groups) > 1:
                        if group is not customer.groups[1]:
                            customer.groups.remove(group)
                            customer.groups.insert(1, group)
                else:
                    if len(customer.groups) > 1:
                        customer.groups.insert(1, group)
                    else:
                        customer.groups.append(group)
            else:
                if len(customer.groups) > 1:
                    del customer.groups[1:]


class CustomerPersonImporter(Importer):
    """
    CustomerPerson data importer.
    """
    model_class = model.CustomerPerson
    supported_fields = [
        'uuid',
        'customer_uuid',
        'person_uuid',
        'ordinal',
        ]


class VendorImporter(Importer):
    """
    Vendor data importer.
    """
    model_class = model.Vendor
    simple_fields = [
        'uuid',
        'id',
        'name',
        'special_discount',
        ]
    phone_fields = [
        'phone_number',
        'phone_number_2',
        'fax_number',
        'fax_number_2',
        ]
    contact_fields = [
        'contact_name',
        'contact_name_2',
        ]
    complex_fields = [
        'email_address',
        ]

    @property
    def supported_fields(self):
        return (self.simple_fields + self.phone_fields + self.contact_fields
                + self.complex_fields)

    def cache_query_options(self):
        options = []
        for field in self.phone_fields:
            if field in self.fields:
                options.append(joinedload(model.Vendor.phones))
                break
        for field in self.contact_fields:
            if field in self.fields:
                options.append(joinedload(model.Vendor._contacts))
                break
        if 'email_address' in self.fields:
            options.append(joinedload(model.Vendor.email))
        return options

    def normalize_record(self, data):
        self.string_or_null(data, 'id', 'name', 'email_address',
                            'phone_number', 'phone_number_2',
                            'fax_number', 'fax_number_2',
                            'contact_name', 'contact_name_2')
        self.prioritize_2(data, 'phone_number')
        self.prioritize_2(data, 'fax_number')
        self.prioritize_2(data, 'contact_name')

    def normalize_instance(self, vendor):
        data = super(VendorImporter, self).normalize_instance(vendor)

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in vendor.phones:
                if phone.type == 'Voice':
                    data['phone_number'] = phone.number
                    break

        if 'phone_number_2' in self.fields:
            data['phone_number_2'] = None
            first = False
            for phone in vendor.phones:
                if phone.type == 'Voice':
                    if first:
                        data['phone_number_2'] = phone.number
                        break
                    first = True

        if 'fax_number' in self.fields:
            data['fax_number'] = None
            for phone in vendor.phones:
                if phone.type == 'Fax':
                    data['fax_number'] = phone.number
                    break

        if 'fax_number_2' in self.fields:
            data['fax_number_2'] = None
            first = False
            for phone in vendor.phones:
                if phone.type == 'Fax':
                    if first:
                        data['fax_number_2'] = phone.number
                        break
                    first = True

        if 'contact_name' in self.fields:
            contact = vendor.contact
            data['contact_name'] = contact.display_name if contact else None

        if 'contact_name_2' in self.fields:
            contact = vendor.contacts[1] if len(vendor.contacts) > 1 else None
            data['contact_name_2'] = contact.display_name if contact else None

        if 'email_address' in self.fields:
            email = vendor.email
            data['email_address'] = email.address if email else None

        return data

    def update_instance(self, vendor, data):
        super(VendorImporter, self).update_instance(vendor, data)

        if 'phone_number' in data:
            number = data['phone_number'] or None
            if number:
                found = False
                for phone in vendor.phones:
                    if phone.type == 'Voice':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    vendor.add_phone_number(number, type='Voice')
            else:
                for phone in list(vendor.phones):
                    if phone.type == 'Voice':
                        vendor.phones.remove(phone)

        if 'phone_number_2' in data:
            number = data['phone_number_2'] or None
            if number:
                found = False
                first = False
                for phone in vendor.phones:
                    if phone.type == 'Voice':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    vendor.add_phone_number(number, type='Voice')
            else:
                first = False
                for phone in list(vendor.phones):
                    if phone.type == 'Voice':
                        if first:
                            vendor.phones.remove(phone)
                            break
                        first = True

        if 'fax_number' in data:
            number = data['fax_number'] or None
            if number:
                found = False
                for phone in vendor.phones:
                    if phone.type == 'Fax':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    vendor.add_phone_number(number, type='Fax')
            else:
                for phone in list(vendor.phones):
                    if phone.type == 'Fax':
                        vendor.phones.remove(phone)

        if 'fax_number_2' in data:
            number = data['fax_number_2'] or None
            if number:
                found = False
                first = False
                for phone in vendor.phones:
                    if phone.type == 'Fax':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    vendor.add_phone_number(number, type='Fax')
            else:
                first = False
                for phone in list(vendor.phones):
                    if phone.type == 'Fax':
                        if first:
                            vendor.phones.remove(phone)
                            break
                        first = True

        if 'contact_name' in data:
            if data['contact_name']:
                contact = vendor.contact
                if not contact:
                    contact = model.Person()
                    self.session.add(contact)
                    vendor.contacts.append(contact)
                contact.display_name = data['contact_name']
            else:
                if len(vendor.contacts):
                    del vendor.contacts[:]

        if 'contact_name_2' in data:
            if data['contact_name_2']:
                contact = vendor.contacts[1] if len(vendor.contacts) > 1 else None
                if not contact:
                    contact = model.Person()
                    self.session.add(contact)
                    vendor.contacts.append(contact)
                contact.display_name = data['contact_name_2']
            else:
                if len(vendor.contacts) > 1:
                    del vendor.contacts[1:]

        if 'email_address' in data:
            address = data['email_address'] or None
            if address:
                if vendor.email:
                    if vendor.email.address != address:
                        vendor.email.address = address
                else:
                    vendor.add_email_address(address)
            else:
                if len(vendor.emails):
                    del vendor.emails[:]


class DepartmentImporter(Importer):
    """
    Department data importer.
    """
    model_class = model.Department
    supported_fields = [
        'uuid',
        'number',
        'name',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'name')


class SubdepartmentImporter(Importer):
    """
    Subdepartment data importer.
    """
    model_class = model.Subdepartment
    simple_fields = [
        'uuid',
        'number',
        'name',
        'department_uuid',
        ]
    supported_fields = simple_fields + [
        'department_number',
        ]

    def setup(self, progress):
        self.departments = self.cache_model(model.Department, 'number')

    def cache_query_options(self):
        if 'department_number' in self.fields:
            return [joinedload(model.Subdepartment.department)]

    def normalize_record(self, data):
        self.string_or_null(data, 'name')

    def normalize_instance(self, subdepartment):
        data = super(SubdepartmentImporter, self).normalize_instance(subdepartment)
        if 'department_number' in self.fields:
            dept = subdepartment.department
            data['department_number'] = dept.number if dept else None
        return data

    def update_instance(self, subdepartment, data):
        super(SubdepartmentImporter, self).update_instance(subdepartment, data)
        if 'department_number' in self.fields:
            dept = self.departments.get(data['department_number'])
            if not dept:
                dept = model.Department()
                dept.number = data['department_number']
                dept.name = "(auto-created)"
                self.session.add(dept)
                self.departments[dept.number] = dept
            subdepartment.department = dept


class CategoryImporter(Importer):
    """
    Category data importer.
    """
    model_class = model.Category
    supported_fields = [
        'uuid',
        'number',
        'name',
        'department_uuid',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'name')


class FamilyImporter(Importer):
    """
    Family data importer.
    """
    model_class = model.Family
    supported_fields = [
        'uuid',
        'code',
        'name',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'name')


class ReportCodeImporter(Importer):
    """
    ReportCode data importer.
    """
    model_class = model.ReportCode
    supported_fields = [
        'uuid',
        'code',
        'name',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'name')


class BrandImporter(Importer):
    """
    Brand data importer.
    """
    model_class = model.Brand
    supported_fields = [
        'uuid',
        'name',
        ]

    def normalize_record(self, data):
        self.string_or_null(data, 'name')


class ProductImporter(Importer):
    """
    Supposedly generic product data importer, but in practice this is currently
    only coded to support a fairly specific CSV format...
    """
    model_class = model.Product
    simple_fields = [
        'uuid',
        'upc',
        'description',
        'size',
        'department_uuid',
        'subdepartment_uuid',
        'category_uuid',
        'family_uuid',
        'report_code_uuid',
        'brand_uuid',
        'unit_of_measure',
        'not_for_sale',
        ]
    regular_price_fields = [
        'regular_price_price',
        'regular_price_multiple',
        'regular_price_pack_price',
        'regular_price_pack_multiple',
        'regular_price_type',
        'regular_price_level',
        'regular_price_starts',
        'regular_price_ends',
        ]
    sale_price_fields = [
        'sale_price_price',
        'sale_price_multiple',
        'sale_price_pack_price',
        'sale_price_pack_multiple',
        'sale_price_type',
        'sale_price_level',
        'sale_price_starts',
        'sale_price_ends',
        ]
    supported_fields = simple_fields + regular_price_fields + sale_price_fields + [
        'brand_name',
        'department_number',
        'subdepartment_number',
        'category_number',
        'family_code',
        'report_code',
        'vendor_id',
        'vendor_item_code',
        'vendor_case_cost',
        ]

    def setup(self, progress):
        if 'brand_name' in self.fields:
            self.brands = self.cache_model(model.Brand, 'name')
        if 'department_number' in self.fields:
            self.departments = self.cache_model(model.Department, 'number')
        if 'subdepartment_number' in self.fields:
            self.subdepartments = self.cache_model(model.Subdepartment, 'number')
        if 'category_number' in self.fields:
            self.categories = self.cache_model(model.Category, 'number')
        if 'family_code' in self.fields:
            self.families = self.cache_model(model.Family, 'code')
        if 'report_code' in self.fields:
            self.reportcodes = self.cache_model(model.ReportCode, 'code')
        if 'vendor_id' in self.fields:
            self.vendors = self.cache_model(model.Vendor, 'id')

    def cache_query_options(self):
        options = []
        if 'brand_name' in self.fields:
            options.append(joinedload(model.Product.brand))
        if 'department_number' in self.fields:
            options.append(joinedload(model.Product.department))
        if 'subdepartment_number' in self.fields:
            options.append(joinedload(model.Product.subdepartment))
        if 'category_number' in self.fields:
            options.append(joinedload(model.Product.category))
        if 'family_code' in self.fields:
            options.append(joinedload(model.Product.family))
        if 'report_code' in self.fields:
            options.append(joinedload(model.Product.report_code))
        joined_prices = False
        for field in self.regular_price_fields:
            if field in self.fields:
                options.append(joinedload(model.Product.prices))
                options.append(joinedload(model.Product.regular_price))
                joined_prices = True
                break
        for field in self.sale_price_fields:
            if field in self.fields:
                if not joined_prices:
                    options.append(joinedload(model.Product.prices))
                options.append(joinedload(model.Product.current_price))
                break
        if ('vendor_id' in self.fields
            or 'vendor_item_code' in self.fields
            or 'vendor_case_cost' in self.fields):
            options.append(joinedload(model.Product.cost))
        return options

    def normalize_record(self, data):
        self.string_or_null(data, 'brand_name', 'description', 'size', 'unit_of_measure',
                            'vendor_id', 'vendor_item_code')
        self.int_or_null(data, 'family_code', 'report_code')

    def normalize_instance(self, product):
        data = super(ProductImporter, self).normalize_instance(product)
        if 'brand_name' in self.fields:
            data['brand_name'] = product.brand.name if product.brand else None
        if 'department_number' in self.fields:
            data['department_number'] = product.department.number if product.department else None
        if 'subdepartment_number' in self.fields:
            data['subdepartment_number'] = product.subdepartment.number if product.subdepartment else None
        if 'category_number' in self.fields:
            data['category_number'] = product.category.number if product.category else None
        if 'family_code' in self.fields:
            data['family_code'] = product.family.code if product.family else None
        if 'report_code' in self.fields:
            data['report_code'] = product.report_code.code if product.report_code else None

        for field in self.regular_price_fields:
            if field in self.fields:
                price = product.regular_price
                if 'regular_price_price' in self.fields:
                    data['regular_price_price'] = price.price if price else None
                if 'regular_price_multiple' in self.fields:
                    data['regular_price_multiple'] = price.multiple if price else None
                if 'regular_price_pack_price' in self.fields:
                    data['regular_price_pack_price'] = price.pack_price if price else None
                if 'regular_price_pack_multiple' in self.fields:
                    data['regular_price_pack_multiple'] = price.pack_multiple if price else None
                if 'regular_price_type' in self.fields:
                    data['regular_price_type'] = price.type if price else None
                if 'regular_price_level' in self.fields:
                    data['regular_price_level'] = price.level if price else None
                if 'regular_price_starts' in self.fields:
                    data['regular_price_starts'] = price.starts if price else None
                if 'regular_price_ends' in self.fields:
                    data['regular_price_ends'] = price.ends if price else None
                break

        for field in self.sale_price_fields:
            if field in self.fields:
                price = product.current_price
                if 'sale_price_price' in self.fields:
                    data['sale_price_price'] = price.price if price else None
                if 'sale_price_multiple' in self.fields:
                    data['sale_price_multiple'] = price.multiple if price else None
                if 'sale_price_pack_price' in self.fields:
                    data['sale_price_pack_price'] = price.pack_price if price else None
                if 'sale_price_pack_multiple' in self.fields:
                    data['sale_price_pack_multiple'] = price.pack_multiple if price else None
                if 'sale_price_type' in self.fields:
                    data['sale_price_type'] = price.type if price else None
                if 'sale_price_level' in self.fields:
                    data['sale_price_level'] = price.level if price else None
                if 'sale_price_starts' in self.fields:
                    data['sale_price_starts'] = price.starts if price else None
                if 'sale_price_ends' in self.fields:
                    data['sale_price_ends'] = price.ends if price else None
                break

        if 'vendor_id' in self.fields or 'vendor_item_code' in self.fields or 'vendor_case_cost' in self.fields:
            cost = product.cost
            if 'vendor_id' in self.fields:
                data['vendor_id'] = cost.vendor.id if cost else None
            if 'vendor_item_code' in self.fields:
                data['vendor_item_code'] = cost.code if cost else None
            if 'vendor_case_cost' in self.fields:
                data['vendor_case_cost'] = cost.case_cost if cost else None

        return data

    def update_instance(self, product, data):
        super(ProductImporter, self).update_instance(product, data)

        if 'brand_name' in data:
            name = data['brand_name']
            if name:
                brand = self.brands.get(name)
                if not brand:
                    brand = model.Brand()
                    brand.name = name
                    self.session.add(brand)
                    self.brands[brand.name] = brand
                product.brand = brand
            else:
                if product.brand:
                    product.brand = None

        if 'department_number' in data:
            number = data['department_number']
            if number:
                dept = self.departments.get(number)
                if not dept:
                    dept = model.Department()
                    dept.number = number
                    dept.name = "(auto-created)"
                    self.session.add(dept)
                    self.departments[dept.number] = dept
                product.department = dept
            else:
                if product.department:
                    product.department = None

        if 'subdepartment_number' in data:
            number = data['subdepartment_number']
            if number:
                sub = self.subdepartments.get(number)
                if not sub:
                    sub = model.Subdepartment()
                    sub.number = number
                    sub.name = "(auto-created)"
                    self.session.add(sub)
                    self.subdepartments[number] = sub
                product.subdepartment = sub
            else:
                if product.subdepartment:
                    product.subdepartment = None

        if 'category_number' in data:
            number = data['category_number']
            if number:
                cat = self.categories.get(number)
                if not cat:
                    cat = model.Category()
                    cat.number = number
                    cat.name = "(auto-created)"
                    self.session.add(cat)
                    self.categories[number] = cat
                product.category = cat
            else:
                if product.category:
                    product.category = None

        if 'family_code' in data:
            code = data['family_code']
            if code:
                family = self.families.get(code)
                if not family:
                    family = model.Family()
                    family.code = code
                    family.name = "(auto-created)"
                    self.session.add(family)
                    self.families[family.code] = family
                product.family = family
            else:
                if product.family:
                    product.family = None

        if 'report_code' in data:
            code = data['report_code']
            if code:
                rc = self.reportcodes.get(code)
                if not rc:
                    import ipdb; ipdb.set_trace()
                    rc = model.ReportCode()
                    rc.code = code
                    rc.name = "(auto-created)"
                    self.session.add(rc)
                    self.reportcodes[rc.code] = rc
                product.report_code = rc
            else:
                if product.report_code:
                    product.report_code = None

        create = False
        delete = False
        for field in self.regular_price_fields:
            if field in data:
                delete = True
                if data[field]:
                    create = True
                    break
        if create:
            price = product.regular_price
            if not price:
                price = model.ProductPrice()
                product.prices.append(price)
                product.regular_price = price
            if 'regular_price_price' in data:
                price.price = data['regular_price_price']
            if 'regular_price_multiple' in data:
                price.multiple = data['regular_price_multiple']
            if 'regular_price_pack_price' in data:
                price.pack_price = data['regular_price_pack_price']
            if 'regular_price_pack_multiple' in data:
                price.pack_multiple = data['regular_price_pack_multiple']
            if 'regular_price_type' in data:
                price.type = data['regular_price_type']
            if 'regular_price_level' in data:
                price.level = data['regular_price_level']
            if 'regular_price_starts' in data:
                price.starts = data['regular_price_starts']
            if 'regular_price_ends' in data:
                price.ends = data['regular_price_ends']
        elif delete:
            if product.regular_price:
                product.regular_price = None

        create = False
        delete = False
        for field in self.sale_price_fields:
            if field in data:
                delete = True
                if data[field]:
                    create = True
                    break
        if create:
            price = product.current_price
            if not price:
                price = model.ProductPrice()
                product.prices.append(price)
                product.current_price = price
            if 'sale_price_price' in data:
                price.price = data['sale_price_price']
            if 'sale_price_multiple' in data:
                price.multiple = data['sale_price_multiple']
            if 'sale_price_pack_price' in data:
                price.pack_price = data['sale_price_pack_price']
            if 'sale_price_pack_multiple' in data:
                price.pack_multiple = data['sale_price_pack_multiple']
            if 'sale_price_type' in data:
                price.type = data['sale_price_type']
            if 'sale_price_level' in data:
                price.level = data['sale_price_level']
            if 'sale_price_starts' in data:
                price.starts = data['sale_price_starts']
            if 'sale_price_ends' in data:
                price.ends = data['sale_price_ends']
        elif delete:
            if product.current_price:
                product.current_price = None

        if 'vendor_id' in data:
            id_ = data['vendor_id']
            if id_:
                vendor = self.vendors.get(id_)
                if not vendor:
                    vendor = model.Vendor()
                    vendor.id = id_
                    vendor.name = "(auto-created)"
                    self.session.add(vendor)
                    self.vendors[id_] = vendor
                if product.cost:
                    if product.cost.vendor is not vendor:
                        cost = product.cost_for_vendor(vendor)
                        if not cost:
                            cost = model.ProductCost()
                            cost.vendor = vendor
                        product.costs.insert(0, cost)
                else:
                    cost = model.ProductCost()
                    cost.vendor = vendor
                    product.costs.append(cost)
                    # TODO: This seems heavy-handed, but also seems necessary
                    # to populate the `Product.cost` relationship...
                    self.session.add(product)
                    self.session.flush()
                    self.session.refresh(product)
            else:
                if product.cost:
                    del product.costs[:]

        if 'vendor_item_code' in self.fields:
            code = data['vendor_item_code']
            if data.get('vendor_id'):
                if product.cost:
                    product.cost.code = code
                else:
                    log.warning("product has no cost, so can't set vendor_item_code: {0}".format(product))

        if 'vendor_case_cost' in self.fields:
            cost = data['vendor_case_cost']
            if data.get('vendor_id'):
                if product.cost:
                    product.cost.case_cost = cost
                else:
                    log.warning("product has no cost, so can't set vendor_case_cost: {0}".format(product))


class ProductCodeImporter(Importer):
    """
    Data importer for :class:`rattail.db.model.ProductCode`.
    """
    model_class = model.ProductCode
    simple_fields = [
        'uuid',
        'product_uuid',
        'ordinal',
        'code',
        ]
    supported_fields = simple_fields + [
        'product_upc',
        ]

    def setup(self, progress=None):
        if 'product_upc' in self.fields:
            self.products = self.cache_model(model.Product, 'upc')

    def cache_query_options(self):
        if 'product_upc' in self.fields:
            return [joinedload(model.ProductCode.product)]

    def normalize_record(self, data):
        self.string_or_null(data, 'code')

    def normalize_instance(self, code):
        data = super(ProductCodeImporter, self).normalize_instance(code)
        if 'product_upc' in self.fields:
            data['product_upc'] = code.product.upc
        return data

    def update_instance(self, code, data):
        super(ProductCodeImporter, self).update_instance(code, data)

        if 'product_upc' in data and 'product_uuid' not in data:
            upc = data['product_upc']
            assert upc, "Source data has no product_upc value: {0}".format(repr(data))
            product = self.products.get(upc)
            if not product:
                product = model.Product()
                product.upc = upc
                product.description = "(auto-created)"
                self.session.add(product)
                self.products[product.upc] = product
            if 'ordinal' in data:
                code.product = product
            else:
                raise NotImplementedError()


class ProductCostImporter(Importer):
    """
    Data importer for :class:`rattail.db.model.ProductCost`.
    """
    model_class = model.ProductCost
    simple_fields = [
        'uuid',
        'product_uuid',
        'vendor_uuid',
        'preference',
        'code',
        'case_size',
        'case_cost',
        'pack_size',
        'pack_cost',
        'unit_cost',
        'effective',
        ]
    supported_fields = simple_fields + [
        'product_upc',
        'vendor_id',
        'preferred',
        ]

    def setup(self, progress=None):
        if 'product_upc' in self.fields:
            self.products = self.cache_model(model.Product, 'upc')
        if 'vendor_id' in self.fields:
            self.vendors = self.cache_model(model.Vendor, 'id')

    def cache_query_options(self):
        options = []
        if 'product_upc' in self.fields:
            options.append(joinedload(model.ProductCost.product))
        if 'vendor_id' in self.fields:
            options.append(joinedload(model.ProductCost.vendor))
        return options

    def normalize_record(self, data):
        self.string_or_null(data, 'code')

    def normalize_instance(self, cost):
        data = super(ProductCostImporter, self).normalize_instance(cost)
        if 'product_upc' in self.fields:
            data['product_upc'] = cost.product.upc
        if 'vendor_id' in self.fields:
            data['vendor_id'] = cost.vendor.id
        data['preferred'] = cost.preference == 1
        return data
        
    def update_instance(self, cost, data):
        super(ProductCostImporter, self).update_instance(cost, data)

        if 'product_upc' in data and 'product_uuid' not in data:
            upc = data['product_upc']
            assert upc, "Source data has no product_upc value: {0}".format(repr(data))
            product = self.products.get(upc)
            if not product:
                product = model.Product()
                product.upc = upc
                product.description = "(auto-created)"
                self.session.add(product)
                self.products[product.upc] = product
            if not cost.product:
                product.costs.append(cost)
            elif cost.product is not product:
                cost.product.costs.remove(cost)
                product.costs.append(cost)

        if 'vendor_id' in data and 'vendor_uuid' not in data:
            id_ = data['vendor_id']
            assert id_, "Source data has no vendor_id value: {0}".format(repr(data))
            vendor = self.vendors.get(id_)
            if not vendor:
                vendor = model.Vendor()
                vendor.id = id_
                vendor.name = "(auto-created)"
                self.session.add(vendor)
                self.vendors[vendor.id] = vendor
            cost.vendor = vendor

        if 'preferred' in data:
            if data['preferred']:
                if cost.preference != 1:
                    product = cost.product
                    product.costs.remove(cost)
                    product.costs.insert(0, cost)
            else:
                if cost.preference == 1:
                    if len(cost.product.costs) > 1:
                        product = cost.product
                        product.costs.remove(cost)
                        product.costs.append(cost)
