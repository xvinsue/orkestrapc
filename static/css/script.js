const optionMenu = document.querySelector(".select-dropdown"),
    selectBtn = optionMenu.querySelector(".select-btn"),
    content = optionMenu.querySelectorAll(".content-option"),
    contentText = optionMenu.querySelector(".content-text");

    selectBtn.addEventListener("click", () => optionMenu.classList.toggle("active"));
    content.forEach(contentOption => {
        contentOption.addEventListener("click", ()=>{
            let selectedOption = contentOption.querySelector(".content-text").innerText;
            contentText.innerText = selectedOption;
            console.log(selectedOption)
        })
        
    });