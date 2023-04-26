document.addEventListener('DOMContentLoaded', function() {

})

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

function submitPost(event) {
    event.preventDefault();
    post = document.querySelector("#post").value;
    submitbtn = document.querySelector("#submitbtn");
    submitbtn.value = submitbtn.dataset.loading;
    submitbtn.className = "btn btn-primary submitbtn";
    setTimeout(() => {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch("/add-post", {
                method: "POST",
                // mode: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    post: post,
                })
            })
            .then(response => response.json())
            .then(message => {
                submitbtn.value = submitbtn.dataset.value;
                submitbtn.className = "btn btn-primary";
                if (message.message == "Post added successfully") {
                    location.href = "/";
                } else {
                    document.querySelector("#post").value = "";
                    document.querySelector(".result").innerHTML = message.error;
                    console.log(message)
                }
            })
            .catch(error => {
                console.log(error)
            })
    }, 1000);
}

function editPostView(id, event) {
    //where to get the post details and insert it
    var container = event.target.parentElement.parentElement;
    var formcontainer = container.children[6];
    console.log(formcontainer);
    var form = formcontainer.children[0]
    form.method = "POST";
    fetch(`/edit-post/${id}`, {
            method: "GET"
        })
        .then(response => response.json())
        .then(post => {
            formcontainer.style.display = "block"
            form.setAttribute("onSubmit", `editPost(${post.id},event)`)
            var postinput = form.children[1].children[1];
            postinput.value = post.post;
        })
        .catch(error => {
            console.log(error)
        })
}

function editPost(id, event) {
    event.preventDefault()
    var form = event.target;
    var post = form.children[1].children[2].value;
    var submitbtn = document.querySelector("#submitbtn");
    submitbtn.value = submitbtn.dataset.loading;
    submitbtn.className = "btn btn-primary submitbtn";
    setTimeout(() => {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch(`/edit-post/${id}`, {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    post: post,
                })
            })
            .then(response => response.json())
            .then(message => {
                submitbtn.value = submitbtn.dataset.value;
                submitbtn.className = "btn btn-primary";
                if (message.message == "post edited successfully") {
                    var mainpost = form.parentElement.parentElement.children[1];
                    mainpost.innerHTML = `Post: ${post}`;
                    form.parentElement.style.display = "none";
                } else {
                    form.innerHTML = `${message.error},edit again`;
                }
            })
            .catch(error => {
                console.log(error)
            })
    }, 1000);
}

function editRemove(event) {
    form = event.target.parentElement;
    form.style.display = "none";
}

function followUser(event, username) {
    //to follow user
    var el = event.target;
    var follow = document.querySelector(".followers");
    setTimeout(() => {
        fetch(`/follow-user/${username}`, {
                method: "PUT",
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json().then(message => {
                if (response.status == 201) {
                    el.innerHTML = "Unfollow";
                    el.setAttribute("Onclick", `unfollowUser(event,'${username}')`)
                    follow.innerHTML = message.message;
                } else {
                    console.log(message.message);
                }
            }))
            .catch(error => {
                console.log(error)
            })
    }, 500);
}

function unfollowUser(event, username) {
    //to unfollow users
    var el = event.target;
    var follow = document.querySelector(".followers");
    setTimeout(() => {
        fetch(`/unfollow-user/${username}`, {
                method: "PUT",
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json().then(message => {
                if (response.status == 201) {
                    el.innerHTML = "Follow";
                    el.setAttribute("Onclick", `followUser(event,'${username}')`)
                    follow.innerHTML = message.message;
                } else {
                    console.log(message.message);
                }
            }))
            .catch(error => {
                console.log(error)
            })
    }, 500);
}

function like(event, id) {
    //to like a post
    el = event.target;
    var likemessage = el.parentElement.children[3];
    setTimeout(() => {
        fetch(`/likepost/${id}`, {
                method: "PUT",
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
            })
            .then(response => response.json().then(message => {
                if (response.status == 201) {
                    el.innerHTML = "Unlike 💓";
                    el.setAttribute("Onclick", `unlike(event,${id})`)
                    likemessage.innerHTML = message.message;

                } else {
                    console.log(message.message)
                }
            }))
            .catch(error => {
                console.log(error)
            })
    }, 500);
}

function unlike(event, id) {
    //to unlike a post
    el = event.target;
    var likemessage = el.parentElement.children[3];
    setTimeout(() => {
        fetch(`/unlikepost/${id}`, {
                method: "PUT",
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
            })
            .then(response => response.json().then(message => {
                if (response.status == 201) {
                    el.innerHTML = "Like 💓";
                    el.setAttribute("Onclick", `like(event,${id})`)
                    likemessage.innerHTML = message.message;

                } else {
                    console.log(message.message)
                }
            }))
            .catch(error => {
                console.log(error)
            })
    }, 500);
}

function getUrl(urlname, additon) {
    // Generate URL without "id" bit
    var url = `{% url '${urlname} %}`;

    var id = additon;

    // Construct the full URL with "id"
    return url + "/" + id;
}

function getPost(requestedusername, page_type, page_num, username) {
    var postcontainer = document.getElementById("posts");
    fetch(`/get-page/${requestedusername}/${page_type}/${page_num}`, {
            method: "GET",
        })
        .then(response => response.json().then(post => {
            if (response.status == 201) {
                //empty present posts to add new ones
                for (let i = 0; i < postcontainer.children.length; i++) {
                    postcontainer.children[0].remove()
                }
                postcontainer.innerHTML = "";
                for (let pos = 0; pos < post.length; pos++) {
                    //check whether post has been liked
                    fetch(`/liked-post/${post[pos].id}`, {
                            method: "GET",
                        })
                        .then(like => like.json().then(message => {
                            var postmain = document.createElement("div")
                            var h4 = document.createElement("h4");
                            var postcontent = document.createElement("p");
                            var time = document.createElement("p")
                            var likes = document.createElement("p");
                            var button = document.createElement("span");
                            var likebutton = "";
                            var form = document.createElement("div");
                            if (like.status == 201) {
                                likebutton = document.createElement("button");
                                likebutton.className = "likebuttton";
                                if (message.message == true) {
                                    //change to unlike
                                    likebutton.innerHTML = "Unlike 💓";
                                    likebutton.setAttribute("onClick", `unlike(event, ${post[pos].id})`)
                                } else if (message.message == false) {
                                    //change to like
                                    likebutton.innerHTML = "Like 💓";
                                    likebutton.setAttribute("onClick", `like(event, ${post[pos].id})`)
                                }
                                postmain.append(h4, postcontent, time, likes, likebutton, button, form);
                            } else {
                                postmain.append(h4, postcontent, time, likes, button, form);
                            }
                            form.className = "form";
                            var csrftoken = getCookie('csrftoken');
                            form.innerHTML = `<form id="add-post" method="POST" target="stopframe" onSubmit="editPost(${post[pos].id}, event)"><input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}" /><div class="form-group"><label for="post"> Enter your  post: </label><br><textarea class="form-control" name="post" id="post" required></textarea></div><input class="btn btn-primary" id="submitbtn" type="submit" value="Edit post" data-loading="Editing post" data-value="Edit post"></form><button onClick="editRemove(event)">Cancel edit</button>`;
                            postmain.className = "post";
                            h4.innerHTML = `Username:  <a href="/profile/${post[pos].creator}"> ${post[pos].creator} </a>`;
                            postcontent.innerHTML = `Post: ${post[pos].post}`;
                            time.innerHTML = `Time: ${post[pos].time}`;
                            likes.className = "likes";
                            likes.innerHTML = `Likes: ${post[pos].likes}`
                            if (username == post[pos].creator) {
                                button.innerHTML = `<button class="edit_post" onClick="editPostView(${post[pos].id},event)">Edit posts</button>`;
                            } else {
                                button.remove()
                            }
                            postcontainer.append(postmain)
                        }))
                        .catch(error => {
                            console.log(error)
                        })

                }
                //update previous and next buttons
                var prevbtn = document.querySelector(".previous");
                var nextbtn = document.querySelector(".next");
                if (page_num > 1) {
                    prevbtn.setAttribute("onclick", `getPost('${requestedusername}', '${page_type}', ${page_num - 1},'${username}')`)
                }
                if (nextbtn) {
                    nextbtn.setAttribute("onclick", `getPost('${requestedusername}', '${page_type}', ${page_num + 1}, '${username}')`)
                }

                //update number buttons
                document.querySelectorAll(".numbers").forEach(e => {
                    var number = parseInt(e.children[0].innerHTML);
                    e.setAttribute("onclick", `getPost('${requestedusername}', '${page_type}', ${number}, '${username}')`)
                })

            } else if (message.message == "page doesn't exist") {
                //change the innerhtml to page doesn't exist
                console.log("page doesn't exist")
            }
        }))
        .catch(error => {
            console.log(error)
        })
}

function messageView(event, username) {
    var el = event.target;
    var parent = document.querySelector(".message_sidebar");
    if (parent.style.opacity == 0) {
        fetch(`/get-message/${username}`, {
                method: "GET",
            })
            .then(response => response.json().then(message => {
                if (response.status == 201) {
                    parent.style.opacity = "1";
                    parent.classList.remove("message_inactive");
                    parent.classList.add("side_bar_active");
                    const messagecontainer = document.getElementById("messages");
                    messagecontainer.innerHTML = "";
                    document.querySelector(".text-input").value = "";

                    //fill it with messages
                    if (!message.message) {
                        for (let i = 0; i < message.length; i++) {
                            const containdiv = document.createElement("div");
                            containdiv.className = "container-div";
                            const div = document.createElement("div");
                            div.className = "message_single receiver";
                            if (message[i].text != "" && message[i].image != "" && message[i].file != "") {
                                div.innerHTML = `
                                <img src="${message[i].image}" alt="userimage"/>
                                <a href="${message[i].file}"> 📄 </a>
                                <p> ${message[i].text} </p>
                                `
                            } else if (message[i].text != "" && message[i].image != "") {
                                div.innerHTML = `
                                <img src="${message[i].image}" alt="userimage"/>
                                <p> ${message[i].text} </p>
                                `
                            } else if (message[i].text != "" && message[i].file != "") {
                                div.innerHTML = `
                                <a href="${message[i].file}"> 📄 </a>
                                <p> ${message[i].text} </p>
                                `
                            } else if (message[i].image != "" && message[i].file != "") {
                                div.innerHTML = `
                                <img src="${message[i].image}" alt="userimage"/>
                                <a href="${message[i].file}"> 📄 </a>
                                `
                            } else if (message[i].text != "") {
                                div.innerHTML = `
                                <p> ${message[i].text} </p>
                                `
                            } else if (message[i].image != "") {
                                div.innerHTML = `
                                <img src="${message[i].image}" alt="userimage"/>
                                `
                            } else if (message[i].file != "") {
                                div.innerHTML = `
                                <a href="${message[i].file}"> 📄 </a>
                                `
                            }
                            containdiv.append(div);
                            messagecontainer.append(containdiv);
                        }
                    }

                } else {
                    console.log(message.message);
                }
            }))
            .catch(error => {
                console.log(error)
            })

    } else if (parent.style.opacity == 1) {
        parent.style.opacity = "0";
        parent.classList.remove("side_bar_active");
        parent.classList.add("message_inactive");
    }
}

function addMessage(text, file, image) {
    var parent = document.getElementById("messages");
    var containerdiv = document.createElement("div");
    var div = document.createElement("div");
    div.className = "message sent bg-warning";
    if (file == "" && image == "") {
        div.innerHTML = `
            <p> ${text} </p>
        `
    } else if (file == "") {
        div.innerHTML = `
            <img src="${image}" alt="userimage"/>
            <p> ${text} </p>
        `
    } else if (image == "") {
        div.innerHTML = `
            <a href="${file}"> 📄 </a>
            <p> ${text} </p>
        `
    } else {
        div.innerHTML = `
            <img src="${image}" alt="userimage"/>
            <a href="${file}"> 📄 </a>
            <p> ${text} </p>
        `
    }
    containerdiv.append(div);
    parent.append(containerdiv);
}

function sendMessage(event, username) {
    event.preventDefault()
    const el = event.target;
    const textmessage = document.querySelector("[name='text_message']").value;
    var imagemessage = document.querySelector("[name='text_image']");
    var filemessage = document.querySelector("[name='text_file']");
    const csrftoken = document.querySelector("[name='csrfmiddlewaretoken']").value;
    if (textmessage == "") {
        var error = document.getElementById("error");
        if (error) {
            error.innerHTML = "Nothing was submitted";
            console.log("not working");
        } else {
            var error = document.createElement("p");
            error.id = "error"
            error.className = "text-danger";
            error.innerHTML = "Nothing was submitted";
            console.log(error);
            el.append(error);
            el.insertBefore(error, el.children[0]);
        }
    } else {
        var parent = document.getElementById("messages");
        var containerdiv = document.createElement("div");
        var div = document.createElement("div");
        div.className = "message rceiver bg-warning";
        if (filemessage.value == "" && imagemessage.value == "") {
            div.innerHTML = `
                <p> ${textmessage} </p>
            `
        } else if (filemessage.value == "") {
            div.innerHTML = `
                <img src="${imagemessage.value}" alt="userimage"/>
                <p> ${textmessage} </p>
            `
        } else if (imagemessage.value == "") {
            div.innerHTML = `
                <a href="${filemessage.value}"> 📄 </a>
                <p> ${textmessage} </p>
            `
        } else {
            div.innerHTML = `
                <img src="${imagemessage.value}" alt="userimage"/>
                <a href="${filemessage.value}"> 📄 </a>
                <p> ${textmessage} </p>
            `
        }
        containerdiv.append(div);
        parent.append(containerdiv);
        var file = "";
        var image = "";
        var data = new FormData()
        data.append("text", textmessage)
        if (filemessage.value != "") {
            filemessage = filemessage.files[0];
            let reader = new FileReader()
            reader.readAsDataURL(filemessage)
            file = reader.result;
        } else if (filemessage.value == "") {
            file = "";
        } else if (imagemessage.value != "") {
            imagemessage = imagemessage.files[0];
            let reader = new FileReader()
            reader.readAsDataURL(imagemessage)
            image = reader.result;
        } else if (imagemessage.value == "") {
            image = "";
        }
        setTimeout(() => {
            fetch(`/send-message/${username}`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken,
                    },
                    body: JSON.stringify({
                        "text": textmessage,
                        "file": file,
                        "image": image,
                    })
                })
                .then(response => response.json().then(message => {
                    if (response.status == 201) {
                        document.querySelector("[name='text_message']").value = "";
                        div.className = "message sent bg-success";
                    } else {
                        console.log(message.message);
                    }
                }))
                .catch(error => {
                    console.log(error);
                })
        }, 1000);
    }
}