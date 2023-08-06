{% extends "partials/layout.fluid.html.tpl" %}
{% block htitle %}{{ owner.description }} / {% block title %}{% endblock %}{% endblock %}
{% block links %}
    {% if section == "admin" %}
        <a class="selected" href="{{ url_for('admin.index') }}">home</a>
    {% else %}
        <a href="{{ url_for('admin.index') }}">home</a>
    {% endif %}
    {% if section == "options" %}
        <a class="selected" href="{{ url_for('admin.options') }}">options</a>
    {% else %}
        <a href="{{ url_for('admin.options') }}">options</a>
    {% endif %}
    {% if section == "status" %}
        <a class="selected" href="{{ url_for('admin.status') }}">status</a>
    {% else %}
        <a href="{{ url_for('admin.status') }}">status</a>
    {% endif %}
    <div class="separator"></div>
    {% for _section, models in models_d.items() %}
        {% for _model in models %}
            {% if section == "models" and model and model._name() == _model._name() %}
                <a class="selected"
                   href="{{ url_for('admin.show_model', model = _model._name()) }}">{{ _model._name() }}</a>
            {% else %}
                <a href="{{ url_for('admin.show_model', model = _model._name()) }}">{{ _model._name() }}</a>
            {% endif %}
        {% endfor %}
        <div class="separator"></div>
    {% endfor %}
{% endblock %}
