{% extends "partials/admin.simple.html.tpl" %}
{% block title %}Login{% endblock %}
{% block content %}
    <div class="login-panel">
        <h1>Sign up</h1>
        <h3>Create you new account on <strong>{{ owner.description }}</strong></h3>
        <div class="quote error">
            {{ error }}
        </div>
        <form action="{{ url_for('admin.create_account') }}" method="post" class="form">
            <input type="hidden" name="next" value="{{ next|default('', True) }}" />
            <div class="input">
                <input type="text" class="text-field small focus" name="username" value="{{ account.username }}"
                       placeholder="username" data-error="{{ errors.username }}" />
            </div>
            <div class="input">
                <input type="text" class="text-field small" name="email" value="{{ account.email }}"
                       placeholder="email" data-error="{{ errors.email }}"/>
            </div>
            <div class="input">
                <input type="password" class="text-field small" name="password" placeholder="password"
                        data-error="{{ errors.password }}" />
            </div>
            <div class="input">
                <input type="password" class="text-field small" name="password_confirm" placeholder="confirm password"
                       data-error="{{ errors.password_confirm }}" />
            </div>
            <div class="buttons">
                <span class="button medium button-color button-blue" data-submit="true">Sign up</span>
            </div>
            <div class="new">
                <span>or</span>
                <a href="{{ url_for('admin.login') }}">return to sign in</a>
            </div>
        </form>
    </div>
{% endblock %}
