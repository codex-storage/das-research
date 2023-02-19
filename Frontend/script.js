let section1 = document.querySelector('.sec1');
let section2 = document.querySelector('.sec2');
let section3 = document.querySelector('.sec3');
let section4 = document.querySelector('.sec4');
let sections = [section1, section2, section3, section4];

let icon1 = document.querySelector(".sec1 i");
let icon2 = document.querySelector(".sec2 i");
let icon3 = document.querySelector(".sec3 i");
let icon4 = document.querySelector(".sec4 i");
let icons = [icon1, icon2, icon3, icon4];

let par1 = document.querySelector(".p1");
let par2 = document.querySelector(".p2");
let par3 = document.querySelector(".p3");
let par4 = document.querySelector(".p4");
let paragraphs = [par1, par2, par3, par4];

section1.style.cssText = "background: #eee5fdea; border-top-left-radius: 50%; border-bottom-left-radius: 50%; cursor: pointer; transition: all 0.5s ease-in-out;"
icon1.style.cssText = "opacity: 1; color: #160f25;"

sections.forEach(section =>{
    section.addEventListener("click", function(){
        sections.forEach(s =>{
            s.style.cssText = "background: none; border-top-left-radius: 0%; border-bottom-left-radius: 0%;"
            icons[sections.indexOf(s)].style.cssText = "color: #b9aecf; opacity: 0.7;"
            paragraphs[sections.indexOf(s)].style.display = "none";
        });
        section.style.cssText = "background: #eee5fdea; border-top-left-radius: 50%; border-bottom-left-radius: 50%; cursor: pointer; transition: all 0.5s ease-in-out;"
        icons[sections.indexOf(section)].style.cssText = "opacity: 1; color: #160f25;"
        paragraphs[sections.indexOf(section)].style.display = "block";
    });
});