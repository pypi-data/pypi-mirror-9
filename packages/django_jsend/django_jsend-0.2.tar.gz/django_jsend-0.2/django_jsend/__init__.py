# A simple Jsend view for Django
# Copyright (C) 2015 Maikel Martens

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json

from django.views.generic import View
from django.http import HttpResponse

class JsendView(View):
	"""Django view for sending JSON response by the JSend specification

	Specification website: http://labs.omniti.com/labs/jsend

	"""
	SUCCESS = 'success'
	ERROR = 'error'
	FAIL = 'fail'
	allow_cors = False

	def __init__(self, *args, **kwargs):
		super(JsendView, self).__init__(*args, **kwargs)
		self.status = self.SUCCESS
		self.data = ""
		self.message = ""

	def handle_request(self, request):
		"""Overide this in your class for handling the request"""
		pass

	def _handle_request(self, request, *args, **kwargs):
		try:
			data = self.handle_request(request, *args, **kwargs)
		except Exception as e:
			self.status = self.ERROR
			self.message = str(e)

		if self.status == self.ERROR:
			jsend = {
				'status': self.status,
				'message': self.message
			}
		else:
			jsend = {
				'status': self.status,
				'data': data
			}
		response = HttpResponse(json.dumps(jsend), content_type="application/json")
		if self.allow_cors:
			response['Access-Control-Allow-Origin'] = "*"
		return response

	def get(self, request, *args, **kwargs):
		return self._handle_request(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		return self._handle_request(request, *args, **kwargs)