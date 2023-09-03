function formatDate(postCreatedAtString) {
  const utcDateTime = luxon.DateTime.fromISO(postCreatedAtString, { zone: 'utc' });
  const userLocalDateTime = utcDateTime.toLocal();

  const monthAbbreviations = {
    "01": "січня", "02": "лютого", "03": "березня", "04": "квітня", "05": "травня", "06": "червня",
    "07": "липня", "08": "серпня", "09": "вересня", "10": "жовтня", "11": "листопада", "12": "грудня"
  };

  const year = userLocalDateTime.year;
  const month = userLocalDateTime.month.toString().padStart(2, '0');
  const day = userLocalDateTime.day.toString().padStart(2, '0');
  const hour = userLocalDateTime.hour.toString().padStart(2, '0');
  const minute = userLocalDateTime.minute.toString().padStart(2, '0');

  const monthText = monthAbbreviations[month];

  const now = luxon.DateTime.local();
  const day_now = now.day.toString().padStart(2, '0');

  const diff = now.diff(userLocalDateTime);

  const duration = diff.shiftTo('years', 'days', 'hours', 'minutes', 'seconds');

  let formattedTime = '';

  if (duration.years >= 1) {
    formattedTime = `${day} ${monthText}, ${year}`;
  } else if (duration.days >= 1) {
    formattedTime = `${day} ${monthText}, ${hour}:${minute}`;
  } else if (day_now > day) {
    formattedTime = `вчора, ${hour}:${minute}`;
  } else if (duration.hours >= 1) {
    formattedTime = `${duration.hours} год.`;
  } else if (duration.minutes >= 1) {
    formattedTime = `${duration.minutes} хв.`;
  } else {
    const roundedSeconds = Math.round(duration.seconds);
    formattedTime = `${roundedSeconds} сек.`;
  }

  return formattedTime;
}


document.addEventListener('DOMContentLoaded', function() {
    const likePostButtons = document.querySelectorAll('.like-post');
    const likeCommentButtons = document.querySelectorAll('.like-comment');
    const redirect = document.querySelectorAll('.post-button');
    const subscribeButtons = document.querySelectorAll('.subscribe-button');
    const replyOnPost = document.querySelectorAll('.reply-on-post');

    likePostButtons.forEach(button => {
        button.addEventListener('click', function() {
            const user_is_authenticated = this.getAttribute('data-user');
            const postId = this.getAttribute('data-post-id');

            if (user_is_authenticated === 'True') {
                const post_likes_count = document.querySelector(`.post-likes-count[data-post-id="${postId}"]`);
                const post_comments_count = document.querySelector(`.post-comments-count[data-post-id="${postId}"]`);
                const post_info_dot = document.querySelector(`.info-dot[data-post-id="${postId}"]`);
                const verticalLineElement = document.querySelector(`.vl[data-post-id="${postId}"]`);

                fetch(`/like-post/${postId}/`)
                    .then(response => response.json())
                    .then(data => {
                        updateLikeButtonForPost(this, data.is_liked);
                        post_updateCounts(postId, post_likes_count, post_comments_count, post_info_dot, verticalLineElement, data.post_like_count, data.post_comment_count, data.profile_image);
                    });
            } else {
                window.location.href = `/login/?next=/post/${postId}/`
            }
        });
    });

    likeCommentButtons.forEach(button => {
        button.addEventListener('click', function() {
            const user_is_authenticated = this.getAttribute('data-user');
            const postId = this.getAttribute('data-post-id');

            if (user_is_authenticated === 'True') {
                const commentId = this.getAttribute('data-comment-id');
                const comment_likes_count = document.querySelector(`.comment-likes-count[data-comment-id="${commentId}"]`);
                const comment_comments_count = document.querySelector(`.comment-comments-count[data-comment-id="${commentId}"]`);
                const comment_info_dot = document.querySelector(`.info-dot[data-comment-id="${commentId}"]`);

                fetch(`/like-comment/${postId}/${commentId}/`)
                    .then(response => response.json())
                    .then(data => {
                        updateLikeButtonForComment(this, data.is_liked);
                        comment_updateCounts(commentId, comment_likes_count, comment_comments_count, comment_info_dot, data.comment_like_count, data.comment_comment_count);
                    });
            } else {
                window.location.href = `/login/?next=/post/${postId}/`
            }
        });
    });

    redirect.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            window.location.href = `/post/${postId}/`;
        });
    });

    subscribeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.getAttribute('data-user');
            window.location.href = `/subscribe/${userId}/`;
        });
    });

    replyOnPost.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            window.location.href = `/reply/${postId}/`;
        });
    });
});

function updateLikeButtonForPost(button, isLiked) {
    const newIcon = new Image();
    newIcon.alt = 'heart';
    newIcon.className = 'bi pe-none';
    newIcon.width = 25;
    newIcon.height = 25;

    if (isLiked) {
        newIcon.src = `${staticBaseUrl}images/heart-fill.svg`;
    } else {
        newIcon.src = `${staticBaseUrl}images/heart.svg`;
    }

    const existingIcon = button.querySelector('img');
    if (existingIcon) {
        button.replaceChild(newIcon, existingIcon);
    } else {
        button.appendChild(newIcon);
    }
}

function updateLikeButtonForComment(button, isLiked) {
    const newIcon = new Image();
    newIcon.alt = 'heart';
    newIcon.className = 'bi pe-none';
    newIcon.width = 20;
    newIcon.height = 20;

    if (isLiked) {
        newIcon.src = `${staticBaseUrl}images/heart-fill.svg`;
    } else {
        newIcon.src = `${staticBaseUrl}images/heart.svg`;
    }

    const existingIcon = button.querySelector('img');
    if (existingIcon) {
        button.replaceChild(newIcon, existingIcon);
    } else {
        button.appendChild(newIcon);
    }
}

function post_updateCounts(postId, post_likes_count, post_comments_count, post_info_dot, verticalLineElement, likeCount, commentCount, profileImage) {
    const post_commentsAndLikesBlock = document.querySelector(`.comments-and-likes-block[data-post-id="${postId}"]`);
    // const profileImageElement = document.querySelector(`.profile_image[data-post-id="${postId}"]`);

    if (post_commentsAndLikesBlock) {
        if (likeCount > 0 || commentCount > 0) {
            post_commentsAndLikesBlock.style.display = 'block';

            // Оновлення зображення профілю
            // profileImageElement.alt= "user";
            // profileImageElement.width = 10;
            // profileImageElement.height = 10;
            //
            // if (profileImageElement) {
            //     profileImageElement.src = `${staticBaseUrl}${profileImage}`;
            // }

            // Оновлення тексту коментарів
            if (commentCount === 1) {
                post_comments_count.innerHTML = `<span>Одна відповідь</span>`;
            } else if (commentCount > 1) {
                post_comments_count.innerHTML = `<span>${commentCount} відповідей</span>`;
            }

            if (commentCount === 0) {
                post_comments_count.style.display = 'none';
            } else {
                post_comments_count.style.display = 'inline';
            }

            // Оновлення крапки між лайками та коментарями
            if (likeCount > 0 && commentCount > 0) {
                post_info_dot.style.display = 'inline'; // Показати крапку, якщо є і лайки, і коментарі
            } else {
                post_info_dot.style.display = 'none'; // Приховати крапку, якщо немає або лайків, або коментарів
            }

            // Оновлення тексту лайків
            if (likeCount === 1) {
                post_likes_count.innerHTML = `<span>Одна позначка "Подобається"</span>`;
            } else if (likeCount > 1) {
                post_likes_count.innerHTML = `<span>${likeCount} позначок "Подобається"</span>`;
            }

            if (likeCount === 0) {
                post_likes_count.style.display = 'none';
            } else {
                post_likes_count.style.display = 'inline';
            }

            if (commentCount > 0) {
            verticalLineElement.style.display = 'block'; // Показати вертикальну лінію, якщо є і лайки, і коментарі
            } else {
                verticalLineElement.style.display = 'none'; // Приховати вертикальну лінію, якщо немає або лайків, або коментарів
            }

        } else {
            post_commentsAndLikesBlock.style.display = 'none';
        }
    }
}

function comment_updateCounts(commentId, comment_likes_count, comment_comments_count, comment_info_dot, likeCount, commentCount) {
    const comment_commentsAndLikesBlock = document.querySelector(`.comments-and-likes-block[data-comment-id="${commentId}"]`);

    if (comment_commentsAndLikesBlock) {
        if (likeCount > 0 || commentCount > 0) {
            comment_commentsAndLikesBlock.style.display = 'block';

            // Оновлення тексту коментарів
            if (commentCount === 1) {
                comment_comments_count.innerHTML = `<span>Одна відповідь</span>`;
            } else if (commentCount > 1) {
                comment_comments_count.innerHTML = `<span>${commentCount} відповідей</span>`;
            }

            if (commentCount === 0) {
                comment_comments_count.style.display = 'none';
            } else {
                comment_comments_count.style.display = 'inline';
            }

            // Оновлення крапки між лайками та коментарями
            if (likeCount > 0 && commentCount > 0) {
                comment_info_dot.style.display = 'inline'; // Показати крапку, якщо є і лайки, і коментарі
            } else {
                comment_info_dot.style.display = 'none'; // Приховати крапку, якщо немає або лайків, або коментарів
            }

            // Оновлення тексту лайків
            if (likeCount === 1) {
                comment_likes_count.innerHTML = `<span>Одна позначка "Подобається"</span>`;
            } else if (likeCount > 1) {
                comment_likes_count.innerHTML = `<span>${likeCount} позначок "Подобається"</span>`;
            }

            if (likeCount === 0) {
                comment_likes_count.style.display = 'none';
            } else {
                comment_likes_count.style.display = 'inline';
            }

        } else {
            comment_commentsAndLikesBlock.style.display = 'none';
        }
    }
}
