const polygonList = document.querySelectorAll("polygon");
const circleList = document.querySelectorAll("circle");

function showTitlePolygon (e) {
    const title = document.querySelector(".name-location");
    const image = document.querySelector(".name-image");
    title.innerHTML= e.target.dataset.title;
    image.setAttribute("src", "static/img/map/" + e.target.dataset.img);
}

function showTitleCircle (e) {
    const title = document.querySelector(".name-location");
    const image = document.querySelector(".name-image");
    title.innerHTML= e.target.dataset.title;
    image.setAttribute("src", "static/img/map/" + e.target.dataset.img);
}

polygonList.forEach(element => {
    element.addEventListener('mouseover', showTitlePolygon)
});

circleList.forEach(element => {
    element.addEventListener('mouseover', showTitleCircle)
});