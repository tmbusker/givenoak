'use strict';
{
    function init_select_ido_type_by_get() {
        function select_ido_type(event) {
            let url = '/jinji/select_ido_type/'
            url += '?' + 'ido_type=' + event.target.value;
            // console.log('url:', url)
            fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                    let html_data = '<option value="">---------</option>';
                    data.data.forEach(function (row) {
                        html_data += `<option value="${row[0]}">${row[1]}</option>`
                    });
                    const ido_syumoku = document.querySelector('#id_ido_syumoku');
                    // console.log('ido_syumoku:', ido_syumoku.innerHTML);
                    ido_syumoku.innerHTML =html_data;
            }).catch((error) => {
                    console.error('Error:', error);
            });
        }

        const ido_type = document.querySelector('#id_ido_type');
        console.log('id_ido_type', ido_type)
        ido_type.addEventListener('change', select_ido_type, false);
    }

    function init_select_ido_type_by_post() {
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrftoken = getCookie('csrftoken');

        function select_ido_type(event) {
            let url = '/jinji/select_ido_type/'
            // console.log('url:', url)
            const data = {'ido_type': event.target.value}
            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({'data': data})
            })
            .then(response => response.json())
            .then(data => {
                    console.log('data:', data)
                    let html_data = '<option value="">---------</option>';
                    data.data.forEach(function (row) {
                        html_data += `<option value="${row[0]}">${row[1]}</option>`
                    });
                    const ido_syumoku = document.querySelector('#id_ido_syumoku');
                    // console.log('ido_syumoku:', ido_syumoku.innerHTML);
                    ido_syumoku.innerHTML =html_data;
            }).catch((error) => {
                    console.error('Error:', error);
            });
        }

        const ido_type = document.querySelector('#id_ido_type');
        console.log('id_ido_type', ido_type)
        ido_type.addEventListener('change', select_ido_type, false);
    }

    // document.addEventListener("DOMContentLoaded", init_select_ido_type_by_get);
    document.addEventListener("DOMContentLoaded", init_select_ido_type_by_post);
}
