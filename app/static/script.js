document.addEventListener('DOMContentLoaded', function() {
    loadGames();
    setupEventListeners();
});

function setupEventListeners() {
    const userGamesForm = document.getElementById('userGamesForm');
    if (userGamesForm) {
        userGamesForm.addEventListener('submit', handleUserGamesSubmit);
    }
}

async function loadGames() {
    try {
        const response = await fetch('/api/games');
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const games = await response.json();
        displayGames(games);
    } catch (error) {
        console.error('Ошибка загрузки:', error);
        showAlert('Ошибка загрузки списка игр', 'danger');
    }
}

function displayGames(games) {
    const container = document.getElementById('gamesList');
    if (!container) return;
    if (!games || games.length === 0) {
        container.innerHTML = '<p>Игр пока нет</p>';
        return;
    }
    container.innerHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Название</th>
                    <th>Стоимость</th>
                    <th>Жанр</th>
                </tr>
            </thead>
            <tbody>
                ${games.map(function(g) {
                    return '<tr><td>' + g.id + '</td><td><strong>' + g.title + '</strong></td><td>' + g.price + '</td><td>' + g.genre + '</td></tr>';
                }).join('')}
            </tbody>
        </table>
    `;
}

async function handleUserGamesSubmit(e) {
    e.preventDefault();
    var formData = {
        login: document.getElementById('userLogin').value,
        password: document.getElementById('userPassword').value
    };
    try {
        var response = await fetch('/api/user-games', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        var result = await response.json();
        const container = document.getElementById('userGamesResult');
        if (!container) return;

        if (!response.ok) {
            container.innerHTML = '<p class="text-danger">' + (result.error || 'Ошибка аутентификации') + '</p>';
            showAlert(result.error || 'Ошибка аутентификации', 'danger');
            return;
        }

        if (!result.purchased_game) {
            container.innerHTML = '<p>У пользователя нет купленных игр.</p>';
            return;
        }

        const g = result.purchased_game;
        container.innerHTML = ''
            + '<p><strong>Пользователь:</strong> ' + result.user.login + '</p>'
            + '<p><strong>Купленная игра:</strong></p>'
            + '<ul>'
            + '<li><strong>Название:</strong> ' + g.title + '</li>'
            + '<li><strong>Стоимость:</strong> ' + g.price + '</li>'
            + '<li><strong>Жанр:</strong> ' + g.genre + '</li>'
            + '</ul>';
    } catch (err) {
        showAlert('Ошибка запроса к серверу', 'danger');
    }
}

function showTab(tabName) {
    var tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(function(t) { t.classList.remove('active'); });
    var buttons = document.querySelectorAll('.nav-tab');
    buttons.forEach(function(b) { b.classList.remove('active'); });
    var target = document.getElementById(tabName);
    if (target) target.classList.add('active');
    if (event && event.target) event.target.classList.add('active');
    if (tabName === 'games') {
        loadGames();
    }
}

function showAlert(message, type) {
    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-' + type;
    alertDiv.textContent = message;
    var container = document.querySelector('.container');
    if (container) container.insertBefore(alertDiv, container.firstChild);
    setTimeout(function() { alertDiv.remove(); }, 5000);
}
