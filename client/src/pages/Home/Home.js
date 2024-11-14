import React, { useEffect, useState } from 'react';
import { fetchPosts, likePost } from '../../api/posts';
import './Home.css';

function Home() {
  const [posts, setPosts] = useState([]);
  const username = localStorage.getItem("username");

  // Fetch all posts
  useEffect(() => {
    const loadPosts = async () => {
      const response = await fetchPosts();
      setPosts(response);
    };
    loadPosts();
  }, []);

  // Handle like button click
  const handleLike = async (postId) => {
    try {
      const response = await likePost(postId, username);
      if (response.success) {
        alert(response.message);
      } else {
        alert(response.message);
      }
    } catch (error) {
      console.error('Error liking post:', error);
      alert('Failed to like post. Please try again.');
    }
  };

  return (
    <div className="home-container">
      <header className="header">
        <h2 className="header-title">Community Posts</h2>
        <p className="header-subtitle">Join the conversation and engage with the community.</p>
      </header>
      <div className="posts-list">
        {posts.map((post) => (
          <div key={post._id} className="post-card">
            <div className="post-header">
              <p className="post-reputation">User Reputation: {post.User_rep || 0}</p>
            </div>
            <p className="post-text">{post.newsText}</p>
            <div className="post-footer">
              <button
                className="like-button"
                onClick={() => handleLike(post._id)}
              >
                👍 Like
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Home;
