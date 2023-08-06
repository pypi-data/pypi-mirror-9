{% extends "partials/admin.fluid.html.tpl" %}
{% block title %}Admin{% endblock %}
{% block name %}Site administration{% endblock %}
{% block content %}
    <div>
        {% for section, models in models_d.items() %}
            <div class="panel-model">
                <h3>{{ section }}</h3>
                <ul>
                    {% for model in models %}
                        <li>
                            <div class="left">
                                <a class="name" href="{{ url_for('admin.show_model', model = model._name()) }}">{{ model._name() }}</a>
                            </div>
                            <div class="right">
                                <span class="button create" data-link="{{ url_for('admin.new_entity', model = model._name()) }}">create</span>
                                <span class="button update">update</span>
                            </div>
                            <div class="clear"></div>
                        </li>
                    {% endfor %}
                </ul>
             </div>
        {% endfor %}
    </div>
{% endblock %}
