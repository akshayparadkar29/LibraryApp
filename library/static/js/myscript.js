var scrollPosition;

function trackScrollPosition() {
    scrollPosition = window.scrollY;
    console.log("Scroll Position",scrollPosition)
}

window.addEventListener("scroll",trackScrollPosition)

function restoreScrollPosition() {
    window.scrollTo(0,scrollPosition);
}

document.getElementById("buy").addEventListener("click",restoreScrollPosition);
document.getElementById("borrow").addEventListener("click",restoreScrollPosition);
document.getElementById("addtocart").addEventListener("click",function(event){
    event.preventDefault();
    console.log("Button Clicked!");
});
window.addEventListener("load",scrollPosition);
