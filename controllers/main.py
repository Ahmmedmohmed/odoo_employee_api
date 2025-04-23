import json
from odoo import http
from odoo.http import request
import datetime


class EmployeeAPI(http.Controller):

    # endpoint for create
    @http.route('/api/employee/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_employee(self, **kwargs):
        params = json.loads(request.httprequest.data.decode('utf-8'))
        name = params.get('name')
        if not name:
            return {'error': 'Name is required'}

        employee = request.env['hr.employee'].sudo().create({'name': name})
        return {'success': True, 'employee_id': employee.id}

    # endpoint for check_in
    @http.route('/api/attendance/checkin', type='json', auth='user', methods=['POST'], csrf=False)
    def check_in(self, **kwargs):
        params = json.loads(request.httprequest.data.decode('utf-8'))
        employee_id = params.get('employee_id')
        if not employee_id:
            return {'error': 'employee_id is required'}



        request.env['hr.attendance'].sudo().create({
            'employee_id': employee_id,
            'check_in': datetime.datetime.now()
        })
        return {'success': True}

    # endpoint for check_out
    @http.route('/api/attendance/checkout', type='json', auth='user', methods=['POST'], csrf=False)
    def check_out(self, **kwargs):
        params = json.loads(request.httprequest.data.decode('utf-8'))
        employee_id = params.get('employee_id')
        if not employee_id:
            return {'error': 'employee_id is required'}

        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee_id),
            ('check_out', '=', False)
        ], limit=1, order='check_in desc')

        if not attendance:
            return {'error': 'No check-in found for employee'}

        attendance.write({
            'check_out': datetime.datetime.now()
        })
        return {'success': True}

    # endpoint for attendance report
    @http.route('/api/attendance/report', type='json', auth='user', methods=['POST'], csrf=False)
    def attendance_report(self, **kwargs):
        params = json.loads(request.httprequest.data.decode('utf-8'))
        date = params.get('date')
        check_in_limit = params.get('check_in_time')

        if not date or not check_in_limit:
            return {'error': 'date and check_in_time are required'}

        full_datetime = f"{date} {check_in_limit}"

        all_attendance = request.env['hr.attendance'].sudo().search([
            ('check_in', '>=', date),
            ('check_in', '<', f"{date} 23:59:59")
        ])

        on_time = []
        late = []

        for att in all_attendance:
            check_in_str = att.check_in.strftime("%Y-%m-%d %H:%M:%S")
            if check_in_str <= full_datetime:
                on_time.append({'employee': att.employee_id.name, 'check_in': check_in_str})
            else:
                late.append({'employee': att.employee_id.name, 'check_in': check_in_str})

        return {
            'on_time': on_time,
            'late': late
        }
