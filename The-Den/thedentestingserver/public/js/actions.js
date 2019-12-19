function togglePostMenu() {
    let userPost = document.getElementById('user-post');
    let posts = document.getElementById('posts');
    if (userPost.style.display == 'none' || userPost.style.display == '') {
        userPost.style.display = 'block';
        posts.style.display = 'none';
    }
    else {
        userPost.style.display = 'none';
        posts.style.display = 'block';
    }
}

function togglePosts() {
    let posts = document.getElementById('posts');
    let followBox = document.getElementById('follow-box');
    let usersDiv = document.getElementById('users');

    if (posts.style.display == '') {
        posts.style.display = 'none';
        followBox.style.display = 'block';
    }
    else {
        followBox.style.display = 'none';
        posts.style.display = '';
    }
    
    usersDiv.style.display = 'none';
}

function post() {
    let captionArea = document.getElementById('caption');
    let captionText = captionArea.value;

    if (captionText.trim() != '') {
        let XHR = new XMLHttpRequest();
        let formData = new FormData();
        formData.append('caption', captionText);
        XHR.addEventListener('load', function (event) {
            console.log('Sent successfully.');

            let userPost = document.getElementById('user-post');
            let posts = document.getElementById('posts');
            captionArea.value = '';
            posts.style.display = 'block';
            userPost.style.display = 'none';
        });

        XHR.addEventListener('error', function (event) {
            console.log('Caption failed to send.');
        });

        XHR.open('POST', '/post');

        XHR.send(formData);
    }
}

function postComment(postID, user, currentUser) {
    let XHR = new XMLHttpRequest();
    let formData = new FormData();

    let commentText = document.getElementById(postID).getElementsByClassName('comment-area')[0].value;
    formData.append('postID', postID);
    formData.append('user', user);
    formData.append('comment', commentText);

    XHR.addEventListener('load', function (event) {
        if (XHR.status == 200) {
            console.log('Sent successfully.');
            let commentsDiv = document.getElementById(postID).getElementsByClassName('comments')[0];
            let newComment = document.createElement('div');
            newComment.innerText = currentUser + ': ' + commentText;
            newComment.className = 'comment';
            commentsDiv.appendChild(newComment);
            document.getElementById(postID).getElementsByClassName('comment-area')[0].value = '';
        }
    });

    XHR.addEventListener('error', function (event) {
        console.log('Comment failed to send.');
    });

    XHR.open('POST', '/comment');

    XHR.send(formData);
}

function toggleCommentMenu(postID) {
    let commentDiv = document.getElementById(postID).getElementsByClassName('comment-div')[0];

    let display = commentDiv.style.display;
    if (display == 'none' || display == '')
        commentDiv.style.display = 'block';
    else commentDiv.style.display = 'none';
}

function toggleFollowMenu() {
    console.log("Toggled follow menu");
    togglePosts();
}

function Follow(username) {
    // if (username.trim() != '') {
    let XHR = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('username', username);
    // let formData = new FormData();
    XHR.addEventListener('load', function (event) {
        if (XHR.status == 200) {
            //TODO: Update the main page with the users posts
            console.log(XHR.response);
            //Reload the follow query
            userQuery(document.getElementById('follow-box').value);
        }
        else {
            console.log('Follow query failed to send.');
        }
    });

    XHR.open('POST', '/follow');

    XHR.send(formData);
    // }
}

function Unfollow(username) {
    let XHR = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('username', username);
    // let formData = new FormData();
    XHR.addEventListener('load', function (event) {
        if (XHR.status == 200) {
            //TODO: Append a users menu
            console.log(XHR.response);
            userQuery(document.getElementById('follow-box').value);
        }
        else {
            console.log('Unfollow query failed to send.');
        }
    });

    XHR.open('POST', '/unfollow');

    XHR.send(formData);
}

function userQuery(prefix) {
    let usersDiv = document.getElementById('users');
    usersDiv.style.display = 'block';
    
    if (prefix.trim() != '') {
        let XHR = new XMLHttpRequest();
        // let formData = new FormData();
        XHR.addEventListener('load', function (event) {
            if (XHR.status == 200) {
                if (XHR.response != '') {
                    //TODO: Append a users menu
                    console.log(XHR.response);
                    let usersFromServer = JSON.parse(XHR.responseText)/*Text.split(',')*/;
                    usersDiv.innerHTML = '';
                    for (let i = 0; i < usersFromServer.length; i++) {
                        let user = usersFromServer[i];
                        console.log(user);
                        // console.log(Object.keys(JSON.parse(user)));
                        usersDiv.innerHTML += getUserDisplayHTML(user.username, user.following);
                    }
                }
                else {
                    usersDiv.innerHTML = '';
                }
            }
            else {
                console.log('Follow query failed to send.');
            }
        });

        XHR.open('GET', '/user-query?prefix=' + prefix);

        XHR.send();
    }
    else {
        usersDiv.innerHTML = '';
    }
}

function getUserDisplayHTML(username, followingStatus) {
    let display = '<ul class="user"><li class="username">USERNAME</li><input type="button" class="follow-button" value="Follow" onclick="Follow(\'USERNAME\')"></ul>';
    return !followingStatus ? display.replace(/USERNAME/g, username) : display.replace(/USERNAME/g, username).replace(/Follow/g, "Unfollow");
}