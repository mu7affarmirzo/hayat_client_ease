'use strict'
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('floatingPassword');
const loginButton = document.getElementById('loginButton');

if (togglePassword) {
    togglePassword.addEventListener('click', function () {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
    });
}

const checkItem = document.querySelectorAll('#check_item')
const checkName = document.querySelector('#check_text-1')
const checkText = document.querySelector('#check_text-2')
const checkId = document.querySelector('#check_text-3')
const checkSeria = document.querySelector('#check_seria')
const checkPrice = document.querySelector('#check_price')
const checkDate = document.querySelector('#check_date')
const checkRes = document.querySelector('#check_res')
const checkNum1 = document.querySelector('#check_num1')
const checkNum2 = document.querySelector('#check_num2')
const checkNum3 = document.querySelector('#check_num3')
const checkNum4 = document.querySelector('#check_num4')

checkItem.forEach(function (row) {
    row.addEventListener('click', function () {
        var itemId = this.dataset.itemId;
        fetch(`http://localhost:8080/render/warehouse/cheque-popup/${Number(itemId)}`)
            .then(res => res.json())
            .then(data => {
                console.log(data)
                data.forEach(item => {
                    // checkName.value=item.name
                    checkId.value = item.id
                    checkName.defaultValue = item.name
                    checkRes.value = item.in_stock
                    checkPrice.value = item.price
                    checkDate.value = item.expire_date
                    checkText.value = item.company__name
                    checkSeria.value = item.seria
                })
            })
            .catch(err => {
                console.error('Error', err)
            })
    });
});


const checksOfficeInput = document.querySelector('#checks_office')
const checksOfficeModals = document.querySelectorAll('#checks-office-modal')
const checksOfficeId = document.querySelector('#checks-office-id')

checksOfficeModals.forEach(function (checksOfficeModal) {
    checksOfficeModal.onclick = () => {
        var itemId = checksOfficeModal.dataset.itemId;
        checksOfficeId.textContent = Number(itemId)
        checksOfficeInput.value = checksOfficeModal.textContent.trim()
        checksOfficeInput.defaultValue = checksOfficeModal.textContent.trim()
    }
})

