============================
Inline forms with bootstrap3
============================

Form-inline-bootstrap a simple Django app to create form with forsets. 
Use with crispy-forms. 

Quick start
-----------

1. Add 'django_form_inline__bootstrap3' to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'crispy_forms',
        'easy_formsets_bootstrap'
    )

2.  EXAMPLE
    models.py
        class Company(models.Model):
            name = models.CharField(max_length=250)

        class Employe(models.Model):
            name = models.CharField(max_length=250)
            company = models.ForeignKey(Company, related_name='employes')

    forms.py
        class FormMixin(object):
            def __init__(self, *args, **kwargs):
                super(FormMixin, self).__init__(*args, **kwargs)
                self.helper = FormHelper()
                self.helper.form_tag = False


        class CompanyForm(FormMixin, forms.ModelForm):
            class Meta:
                model = Company



        class EmployeForm(FormMixin, forms.ModelForm):
            class Meta:
                model = Employe


        EmplyeFormSet = inlineformset_factory(Company, Employe, form=EmployeForm, extra=1)

    views.py

        class CompanyFormMixin(object):
            model = Company
            formsets_class = [EmployeFormSet]
            form_class = CompanyForm

        class CompanyCreate(CompanyFormMixin, FormsetMixin, CreateView):
            pass


        class CompanyUpdate(CompanyFormMixin, FormsetMixin, UpdateView):
            is_update_view = True

    company_form.html
        /* here need jquery <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script> /*
        {% load form_inlines %}
        {% load crispy_forms_tags %}
        <form action="" method="post" enctype="multipart/form-data">
        {{ form.errors|as_crispy_errors }}
            {% main_form form formsets %}

            {% render_formsets formsets %}


          <div class="form-actions col-md-24">
             <button type="submit" class="btn btn-primary">Save</button>
           </div>
         </form>

        {% empty_formsets formsets %}
3. profit
