fetch("./movies.json")
    .then(response => response.json())
    .then(myMovies => loadMovies(myMovies));

function loadMovies(myMovies) {
    var CardMovie = document.getElementById("col");
    var checkboxes = [];
    var cards = [];
    for (var i = 0; i < myMovies.movies.length; i++) {
        let title = myMovies.movies[i].title;
        let year = myMovies.movies[i].year;
        let url = myMovies.movies[i].url;
        let AddCardMovie = document.createElement("div");
        AddCardMovie.classList.add("col");
        let checkbox = "checkbox" + i.toString();
        let card = "card" + i.toString();
        AddCardMovie.innerHTML = `
            <input type="checkbox" id=${checkbox} class="form-check-input" checked>
            <label for=${checkbox} class="form-check-label">Show Image ${i+1}</label>
                <div id=${card} class="card shadow-sm">
                <img src=${url} class="card-img-top" alt="..."/>
                    <div class="card-body">
                    <p class="card-text"><strong>${title}</strong><br/>${year}</p>
                </div>
            </div>`;
        CardMovie.appendChild(AddCardMovie);

        let cbox = document.getElementById(checkbox);
        let ccard = document.getElementById(card);
        checkboxes.push(cbox);
        cards.push(ccard);
    }
    checkboxes.forEach((checkboxParam, index) => {
    checkboxParam.addEventListener("change", () => {
        cards[index].style.display = checkboxParam.checked ? "block" : "none";
        });
    6});

}


