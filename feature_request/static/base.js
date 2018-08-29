function BaseViewModel() {
    let self = this;
    self.URI = '/api/v1';
    self.requestsURI = `${self.URI}/request/`;
    self.requests = ko.observableArray();
    self.clients = ko.observableArray();
    self.products = ko.observableArray();
    self.clients_object = {};
    self.products_object = {};

    self.get_all_requests = function () {

        if (self.requests().length > 0) {
            self.requests.removeAll();
        }
        // get all feature requests
        self.ajax(self.requestsURI + "all", 'GET', false).done(function (data) {

            for (let i = 0; i < data.length; i++) {
                self.requests.push({
                    id: ko.observable(data[i].id),
                    title: ko.observable(data[i].title),
                    description: ko.observable(data[i].description),
                    client_priority: ko.observable(data[i].client_priority),
                    created: ko.observable(moment(data[i].created).format('LL')),
                    targeted_date: ko.observable(moment(data[i].targeted_date).format('LL')),
                    product: ko.observable(self.products_object[data[i].product]),
                    client: ko.observable(self.clients_object[data[i].client]),
                });
            }

        });
    };

    self.ajax = function (uri, method, cache = true, back = false, data) {
        let request = {
            url: uri,
            type: method,
            contentType: "application/json",
            accepts: "application/json",
            cache: cache,
            dataType: 'json',
            data: JSON.stringify(data),
            success: function (response) {


                if (back) (window.location = "/");

            },
            error: function (jqXHR) {
                console.log("ajax error " + jqXHR.status);
            }
        };
        return $.ajax(request);
    };

    self.create = function (formElement) {
        // If the form data is valid, post the serialized form data to the web API.
        // This is the function that is called on each element of the array.
        let json_data = {};

        $.each($(formElement).serializeArray(), function (i, field) {
            json_data[field.name] = field.value
        });
        let t_date = moment(json_data['targeted_date']);

        if (moment() < t_date) {

            self.ajax(self.requestsURI, 'POST', false, false, json_data).done(function () {
                $('#request_modal_create').modal('hide');
                $("#request_modal_create.modal input").val("");
                $("#request_modal_create.modal textarea").val("");
                $(".alert-warning").fadeOut();

                self.get_all_requests()
            });
        } else {
            $(".alert-warning").text("The target date is old. should be in the future.").fadeIn();

            // alert('Target Date is old. date should be in the future.')
        }

    };

    self.deleteRequest = function () {
        let id = document.getElementById('request_id_edit').value;
        self.ajax(self.requestsURI + id, 'DElETE', false, false).done(function () {
            $('#request_modal_edit').modal('hide');

            self.get_all_requests()

        })
    };

    self.setForm = function (req) {

        document.getElementById('request_title').innerHTML = 'Feature Request Priority #' + req.client_priority();
        document.getElementById('request_id_edit').value = req.id();
        document.getElementById('title_edit').value = req.title();
        document.getElementById('description_edit').value = req.description();
        document.getElementById('client_edit').value = req.client();
        document.getElementById('product_edit').value = req.product();
        document.getElementById('targeted_date_edit').value = req.targeted_date();
    };


    if (self.clients.length === 0) {
        // get all client
        self.ajax(self.URI + "/clients", 'GET', true).done(function (data) {
            self.clients(data);

            for (let i = 0; i < data.length; i++) {
                self.clients_object[data[i].id] = data[i].name;
            }


        });
    }
    if (self.products.length === 0) {
        // get all client
        self.ajax(self.URI + "/products", 'GET', true).done(function (data) {
            self.products(data);
            for (let i = 0; i < data.length; i++) {
                self.products_object[data[i].id] = data[i].name;
            }

        });
    }

    self.get_all_requests()
}

ko.applyBindings(new BaseViewModel(), $('#main')[0]);

