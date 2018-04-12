# -*- coding: utf-8 -*-

import os
import pathlib
import shutil
from flask import current_app
from iota import Iota, Transaction
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from iota.crypto.addresses import AddressGenerator
from .extensions import db
from utils.iota import address_balance, address_checksum, make_transfer
from utils.hash import get_checksum, verify_checksum
from utils.io import get_extension, get_name_without_extension, allowed_file
from datetime import datetime


class IOTAAddress(db.Document):
    """
    IOTA Address model
    """
    created_at = db.DateTimeField(default=datetime.now(), required=True)
    index = db.IntField(required=True)
    address = db.StringField(required=True)
    balance = db.IntField(required=True, default=0)
    checksum = db.StringField(required=True)

    def update_balance(self):
        """
        Update address balance
        """
        self.balance = address_balance(current_app.config['IOTA_HOST'], self.address)
        self.save()


class IOTAAccount(db.Document):
    """
    IOTA Account model
    """
    meta = {
        'abstract': True,
    }
    created_at = db.DateTimeField(default=datetime.now(), required=True)
    seed = db.StringField(required=True, default='')
    addresses = db.ListField(db.ReferenceField(IOTAAddress))
    f_index = db.IntField(required=True, default=0)
    l_index = db.IntField(required=True, default=0)

    @property
    def balance(self):
        """
        Return account balance
        """
        t = 0
        for a in self.addresses:
            a.update_balance()
            t += a.balance

        return t

    def _save_fal_balance(self, f_index=0, l_index=0):
        """
        Update f_index and l_index

        :param f_index:
        :param l_index:
        :return:
        """
        if f_index > 0 and l_index > 0:
            self.f_index = f_index
            self.l_index = l_index

        elif f_index > 0:
            self.f_index = f_index
        elif l_index > 0:
            self.l_index = l_index

    def _update_fal_balance(self):
        """
        Update fal balance

        :return:
        """
        index_with_value = []
        for a in self.addresses:
            if a.balance > 0:
                index_with_value.append(a.index)

        if len(index_with_value) > 0:
            f_index = min(index_with_value)
            l_index = max(index_with_value)
            self._save_fal_balance(f_index, l_index)

    def _generate_addresses(self, count):
        """
        Generate addresses for user

        :param count:
        """
        index_list = [-1]
        for i in range(0, len(self.addresses)):
            index_list.append(self.addresses[i].index)

        if max(index_list) == -1:
            start_index = 0
        else:
            start_index = max(index_list) + 1

        generator = AddressGenerator(self.seed)
        generated = generator.get_addresses(start_index, count)
        i = 0

        while i < count:
            index = start_index + i
            address = address_checksum(str(generated[i]))
            balance = address_balance(current_app.config['IOTA_HOST'], address)
            addr = IOTAAddress(
                index=index,
                address=str(address),
                balance=balance,
                checksum=str(get_checksum(address, self.seed))
            )
            addr.save()
            self.addresses.append(addr)
            i += 1
        self.save()

    @property
    def deposit_address(self):
        """
        Return deposit address of account
        :return:
        """
        if self.l_index == 0:
            if len(self.addresses) > 0:
                return self.addresses[0]

            for a in self.addresses:
                integrity = verify_checksum(a.checksum, a.address, self.seed)
                if a.index > self.l_index and integrity:
                    return a
                elif not integrity:
                    raise Exception('Integrity error')

            self._generate_addresses(1)
            for a in self.addresses:
                integrity = verify_checksum(a.checksum, a.address, self.seed)
                if a.index > self.l_index and integrity:
                    return a

    def get_transfers(self):
        """
        Get transactions

        :return:
        """
        api = Iota(current_app.config['IOTA_HOST'], self.seed)
        result = []

        for a in self.addresses:
            t = api.find_transactions(addresses=[a.address])
            for th in t['hashes']:
                gt = api.get_trytes([th])
                txn = Transaction.from_tryte_string(gt['trytes'][0])
                result.append(txn)

        return result


class File(db.Document):
    """
    File model
    """
    created_at = db.DateTimeField(default=datetime.now(), required=True)
    name = db.StringField(required=True)
    path = db.StringField(required=True)
    extension = db.StringField(required=True)


class Campus(IOTAAccount):
    """
    Campus model
    """
    name = db.StringField(required=True, unique=True)
    description = db.StringField(default='')
    files = db.ListField(db.ReferenceField(File))

    @property
    def projects(self):
        """
        Return projects
        """
        return Project.objects(campus=self)

    def add_file(self, data):
        """
        Add file to campus
        """
        base_path = os.path.join(current_app.config['UPLOAD_BASE'], str(self.id))
        pathlib.Path(base_path).mkdir(parents=False, exist_ok=True)

        if allowed_file(current_app.config['ALLOWED_EXTENSIONS'], data.filename):
            base_name = secure_filename(data.filename)
            name = get_name_without_extension(base_name)
            extension = get_extension(base_name)
            path = os.path.join(base_path, base_name)

            data.save(path)

            f = File(
                name=name,
                extension=extension,
                path=path
            )
            f.save()
            self.files.append(f)

        else:
            raise Exception('Extension not allowed')

    def remove_file(self, file):
        """
        Remove file
        """
        if file in self.files:
            try:
                if os.path.exists(file.path):
                    os.remove(file.path)
            except:
                pass

            self.files.remove(file)
            file.delete()

    def delete(self):
        """
        Delete campus
        """
        base_path = os.path.join(current_app.config['UPLOAD_BASE'], str(self.id))
        if os.path.exists(base_path):
            try:
                shutil.rmtree(base_path, ignore_errors=True)
            except:
                pass

        super().delete()


class Section(db.Document):
    """
    Section model
    """
    created_at = db.DateTimeField(default=datetime.now())
    campus = db.ReferenceField(Campus, required=True)
    year = db.IntField(required=True)
    name = db.StringField(required=True)


class Project(db.Document):
    """
    Project model
    """
    created_at = db.DateTimeField(default=datetime.now())
    campus = db.ReferenceField(Campus, required=True)
    name = db.StringField(required=True)
    files = db.ListField(db.ReferenceField(File))

    def add_file(self, data):
        """
        Add file to project
        """
        base_path = os.path.join(current_app.config['UPLOAD_BASE'], str(self.id))
        pathlib.Path(base_path).mkdir(parents=False, exist_ok=True)

        if allowed_file(current_app.config['ALLOWED_EXTENSIONS'], data.filename):
            base_name = secure_filename(data.filename)
            name = get_name_without_extension(base_name)
            extension = get_extension(base_name)
            path = os.path.join(base_path, base_name)

            data.save(path)

            f = File(
                name=name,
                extension=extension,
                path=path
            )
            f.save()
            self.files.append(f)

        else:
            raise Exception('Extension not allowed')

    def remove_file(self, file):
        """
        Remove file
        """
        if file in self.files:
            try:
                if os.path.exists(file.path):
                    os.remove(file.path)
            except:
                pass

            self.files.remove(file)
            file.delete()

    def delete(self):
        """
        Delete project
        """
        base_path = os.path.join(current_app.config['UPLOAD_BASE'], str(self.id))
        if os.path.exists(base_path):
            try:
                shutil.rmtree(base_path, ignore_errors=True)
            except:
                pass

        super().delete()

    @property
    def groups(self):
        """
        Groups
        """
        return Group.objects(project=self)


class User(db.Document):
    """
    User model
    """
    meta = {'allow_inheritance': True}

    created_at = db.DateTimeField(default=datetime.now())
    type = db.StringField(default='user')
    img_uri = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    email = db.StringField()
    username = db.StringField(required=True, unique=True)
    secret_hash = db.StringField()
    scopes = db.ListField(db.StringField())

    @property
    def secret(self):
        return self.secret_hash

    @secret.setter
    def secret(self, pwd):
        self.secret_hash = generate_password_hash(pwd)

    def check_secret(self, pwd):
        if not self.secret_hash:
            return False
        return check_password_hash(self.secret_hash, pwd)


class Facilitator(User, IOTAAccount):
    """
    Facilitator model
    """
    tags = db.ListField(db.StringField())

    @property
    def claims(self):
        """
        Return claims
        """
        oss = Offer.objects(facilitator=self)

        return Claim.objects(offer__in=oss)


class Student(User):
    """
    Student model
    """
    campus = db.ReferenceField(Campus, required=True)
    section = db.ReferenceField(Section, required=True)

    @property
    def groups(self):
        """
        Return groups
        """
        return Group.objects(students__contains=self)


class Group(IOTAAccount):
    """
    Group model
    """
    project = db.ReferenceField(Project, required=True)
    name = db.StringField(required=True)
    students = db.ListField(db.ReferenceField(Student))
    reserved = db.IntField(required=True, default=0)
    files = db.ListField(db.ReferenceField(File))

    def add_file(self, data):
        """
        Add file to Group
        """
        base_path = os.path.join(current_app.config['UPLOAD_BASE'], str(self.id))
        pathlib.Path(base_path).mkdir(parents=False, exist_ok=True)

        if allowed_file(current_app.config['ALLOWED_EXTENSIONS'], data.filename):
            base_name = secure_filename(data.filename)
            name = get_name_without_extension(base_name)
            extension = get_extension(base_name)
            path = os.path.join(base_path, base_name)

            data.save(path)

            f = File(
                name=name,
                extension=extension,
                path=path
            )
            f.save()
            self.files.append(f)

        else:
            raise Exception('Extension not allowed')

    def remove_file(self, file):
        """
        Remove file
        """
        if file in self.files:
            try:
                if os.path.exists(file.path):
                    os.remove(file.path)
            except:
                pass

            self.files.remove(file)
            file.delete()

    @property
    def claims(self):
        """
        Return Claims
        :return:
        """
        return Claim.objects(group=self)

    def delete(self):
        b = self.balance
        if b > 0:
            make_transfer(current_app.config['IOTA_HOST'], {
                'recipient_address': self.project.campus.deposit_address.address,
                'message': 'From EPSI',
                'tag': 'WITHDRAWGROUP',
                'value': b,
                'seed': self.seed,
                'deposit_address': self.deposit_address.address
            })

        base_path = os.path.join(current_app.config['UPLOAD_BASE'], str(self.id))
        if os.path.exists(base_path):
            try:
                shutil.rmtree(base_path, ignore_errors=True)
            except:
                pass

        super().delete()


class Offer(db.Document):
    """
    Offer model
    """
    created_at = db.DateTimeField(default=datetime.now())
    facilitator = db.ReferenceField(Facilitator)
    name = db.StringField(required=True, unique=True)
    tags = db.ListField(db.StringField())
    price = db.IntField(required=True, default=0)
    description = db.StringField()


class Claim(db.Document):
    """
    Claim model
    """
    created_at = db.DateTimeField(default=datetime.now())
    offer = db.ReferenceField(Offer, required=True)
    group = db.ReferenceField(Group)
    status = db.StringField(required=True)
    message = db.StringField(default='')


class Message(db.Document):
    """
    Message model
    """
    created_at = db.DateTimeField(default=datetime.now())
    claim = db.ReferenceField(Claim, required=True)
    user = db.ReferenceField(User, required=True)
    content = db.StringField(required=True)
