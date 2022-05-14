from http import HTTPStatus
from logging import getLogger

from flask import jsonify, request
from flask_jwt_extended import current_user, get_jwt, jwt_required
from flask_restx import Resource

from app.api.v1.account import namespace
from app.api.v1.account.parsers import (authorization_parser,
                                        login_request_parser,
                                        signup_request_parser)
from app.api.v1.account.schemes import LogInArgs, signup_response
from app.database import session_scope
from app.datastore import user_datastore
from app.errors import APIConflictError, ErrorsMessages
from app.models.roles import ProtectedRoleEnum
from app.models.user import User
from app.services.auth import AccountsService
from app.utils import error_processing


@namespace.route('/signup')
class SignUpView(Resource):
    @namespace.doc(
        'signup',
        responses={
            201: 'Пользователь создан',
            400: 'Отсутствует обязательное поле или недостаточная длина пароля',
            409: 'Пользователь с таким адресом электронной почты уже существует!',
        },
    )
    @namespace.expect(signup_request_parser)
    @namespace.marshal_with(signup_response, code=HTTPStatus.CREATED)
    @error_processing(getLogger('SignUpAPIView.post'))
    def post(self):
        """Регистрация пользователя"""
        args = signup_request_parser.parse_args()
        user = User.query.filter_by(email=args['email']).one_or_none()
        if user:
            raise APIConflictError(ErrorsMessages.EMAIL_IS_BUSY.value, args['email'])
        with session_scope():
            new_user = user_datastore.create_user(**args)
            user_datastore.add_role_to_user(new_user, ProtectedRoleEnum.guest.value)

        return new_user, HTTPStatus.CREATED


@namespace.route('/login')
class LoginView(Resource):
    @namespace.doc(
        'login',
        responses={200: 'Авторизация успешна', 401: 'Неверное имя пользователя или пароль'},
    )
    @namespace.expect(login_request_parser)
    @error_processing(getLogger('LoginAPIView.post'))
    @jwt_required(optional=True)
    def post(self):
        """Авторизация пользователя в системе"""
        if current_user:
            return jsonify(f'Пользователь {current_user.email} уже аутентифицирован')

        args = LogInArgs(**login_request_parser.parse_args())
        user = AccountsService.get_authorized_user(email=args.login, password=args.password,)
        accounts_service = AccountsService(user)
        access_token, refresh_token = accounts_service.login(request)
        return jsonify(access_token=access_token, refresh_token=refresh_token)


@namespace.route('/logout')
class LogoutView(Resource):
    @namespace.doc(
        'logout', responses={200: 'Вы вышли из аккаунта', 401: 'Пользователь не авторизован!'},
    )
    @namespace.expect(authorization_parser)
    @error_processing(getLogger('LogoutAPIView.post'))
    @jwt_required()
    def post(self):
        """Выход из пользовательской сессии"""
        jwt = get_jwt()['jti']
        AccountsService.logout(jwt, current_user.id)
        return jsonify(message='Вы вышли из аккаунта')


@namespace.route('/refresh')
class RefreshTokensView(Resource):
    @namespace.doc(
        'refresh',
        response={
            200: 'OK',
            401: 'Пользователь не авторизован или refresh-токен недействительный!',
        },
    )
    @namespace.expect(authorization_parser)
    @error_processing(getLogger('RefreshAPIView.post'))
    @jwt_required(refresh=True)
    def post(self):
        """Получение новой пары токенов в обмен на refresh-токен"""
        refresh_token = get_jwt()['jti']
        account_service = AccountsService(current_user)
        access_token, refresh_token = account_service.refresh_token_pair(refresh_token)
        return jsonify(access_token=access_token, refresh_token=refresh_token)
