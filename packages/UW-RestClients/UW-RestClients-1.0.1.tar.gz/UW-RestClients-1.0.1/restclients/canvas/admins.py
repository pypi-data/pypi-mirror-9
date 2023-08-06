from restclients.canvas import Canvas
from restclients.canvas.users import Users
from restclients.models.canvas import CanvasAdmin
from restclients.exceptions import DataFailureException
from restclients.dao import Canvas_DAO
from urllib import quote, unquote


class Admins(Canvas):
    def get_admins(self, account_id):
        """
        Return a list of the admins in the account.

        https://canvas.instructure.com/doc/api/admins.html#method.admins.index
        """
        params = self._pagination({})
        url = "/api/v1/accounts/%s/admins%s" % (account_id,
                                                self._params(params))

        admins = []
        for data in self._get_resource(url):
            admins.append(self._admin_from_json(data))
        return admins

    def get_admins_by_sis_id(self, sis_account_id):
        """
        Return a list of the admins in the account by sis id.
        """
        return self.get_admins(self._sis_id(sis_account_id))

    def create_admin(self, account_id, user_id, role):
        """
        Flag an existing user as an admin within the account.

        https://canvas.instructure.com/doc/api/admins.html#method.admins.create
        """
        url = "/api/v1/accounts/%s/admins" % account_id
        body = {"user_id": unquote(str(user_id)),
                "role": role,
                "send_confirmation": False}

        data = self._post_resource(url, body)

        return self._admin_from_json(data)

    def create_admin_by_sis_id(self, sis_account_id, user_id, role):
        """
        Flag an existing user as an admin within the account sis id.
        """
        return self.create_admin(self._sis_id(sis_account_id), user_id, role)

    def delete_admin(self, account_id, user_id, role):
        """
        Remove an account admin role from a user.

        https://canvas.instructure.com/doc/api/admins.html#method.admins.destroy
        """
        url = "/api/v1/accounts/%s/admins/%s?role=%s" % (account_id, user_id,
                                                         quote(role))

        response = Canvas_DAO().deleteURL(url, {"Accept": "application/json"})

        if not (response.status == 200 or response.status == 204):
            raise DataFailureException(url, response.status, response.data)

        return True

    def delete_admin_by_sis_id(self, sis_account_id, user_id, role):
        """
        Remove an account admin role from a user for the account sis id.
        """
        return self.delete_admin(self._sis_id(sis_account_id), user_id, role)

    def _admin_from_json(delf, data):
        admin = CanvasAdmin()
        admin.admin_id = data["id"]
        admin.role = data["role"]
        admin.user = Users()._user_from_json(data["user"])
        return admin
