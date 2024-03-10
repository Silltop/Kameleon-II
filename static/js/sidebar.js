document.addEventListener("scroll", action);

function getOffset(el) {
    var _x = 0;
    var _y = 0;
    while (el && !isNaN(el.offsetLeft) && !isNaN(el.offsetTop)) {
        _x += el.offsetLeft - el.scrollLeft;
        _y += el.offsetTop - el.scrollTop;
        el = el.offsetParent;
    }
    return { top: _y, left: _x };
}
let activated = "";

function action() {
    var y = window.scrollY;
    if (y > 400) {
        openNav();
    } else {
        closeNav();
    }
    list_elements.forEach(element => {
        let yt = getOffset(document.getElementById(element)).top;
        let yb = document.getElementById(element).offsetHeight;
        if (y > (yt - 40) & y < (yb + yt - 20)) {
            var str = "a[href='#" + element + "']";

            var slides = document.getElementsByClassName("ehs");
            for (var i = 0; i < slides.length; i++) {
                slides.item(i).style.color = "gray";
            }

            var els = document.querySelectorAll(str);
            activated = els[0].id;

            document.getElementById(activated).style.color = "white";
        }

    });

}

function openNav() {
    document.getElementById("sidenav").style.width = "60px";
    document.getElementById("record-container").style.marginLeft = "60px";
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
function closeNav() {
    document.getElementById("sidenav").style.width = "0";
    document.getElementById("record-container").style.marginLeft = "0";
}