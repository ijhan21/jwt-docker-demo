import { useState, useEffect } from 'react';
import { getMemos, createMemo, updateMemo, deleteMemo, getUserInfo } from '../api';

function Memos({ onLogout }) {
  const [memos, setMemos] = useState([]);
  const [username, setUsername] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    loadUserInfo();
    loadMemos();
  }, []);

  const loadUserInfo = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const user = await getUserInfo(token);
      setUsername(user.username);
    } catch (err) {
      console.error('사용자 정보 로드 실패:', err);
    }
  };

  const loadMemos = async () => {
    try {
      const data = await getMemos();
      setMemos(data);
    } catch (err) {
      console.error('메모 로드 실패:', err);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title || !content) return;

    try {
      await createMemo(title, content);
      setTitle('');
      setContent('');
      loadMemos();
    } catch (err) {
      alert('메모 생성에 실패했습니다.');
    }
  };

  const handleEdit = (memo) => {
    setEditingId(memo.id);
    setEditTitle(memo.title);
    setEditContent(memo.content);
  };

  const handleUpdate = async (id) => {
    try {
      await updateMemo(id, editTitle, editContent);
      setEditingId(null);
      loadMemos();
    } catch (err) {
      alert('메모 수정에 실패했습니다.');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await deleteMemo(id);
      loadMemos();
    } catch (err) {
      alert('메모 삭제에 실패했습니다.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    onLogout();
  };

  return (
    <div className="app">
      <div className="header">
        <h1>메모 앱</h1>
        <div>
          <span style={{ marginRight: '20px' }}>환영합니다, {username}님!</span>
          <button onClick={handleLogout}>로그아웃</button>
        </div>
      </div>

      <div className="memos-container">
        <div className="memo-form">
          <h3>새 메모 작성</h3>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label>제목</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>내용</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary">
              메모 추가
            </button>
          </form>
        </div>

        <div className="memo-list">
          <h3>내 메모 목록</h3>
          {memos.length === 0 ? (
            <div className="no-memos">아직 작성한 메모가 없습니다.</div>
          ) : (
            memos.map((memo) => (
              <div key={memo.id} className="memo-item">
                {editingId === memo.id ? (
                  <>
                    <div className="form-group">
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                      <textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                      />
                    </div>
                    <div className="memo-actions">
                      <button
                        className="btn-save"
                        onClick={() => handleUpdate(memo.id)}
                      >
                        저장
                      </button>
                      <button
                        className="btn-cancel"
                        onClick={() => setEditingId(null)}
                      >
                        취소
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <h4>{memo.title}</h4>
                    <p>{memo.content}</p>
                    <small>
                      작성일: {new Date(memo.created_at).toLocaleString('ko-KR')}
                    </small>
                    <div className="memo-actions">
                      <button className="btn-edit" onClick={() => handleEdit(memo)}>
                        수정
                      </button>
                      <button
                        className="btn-delete"
                        onClick={() => handleDelete(memo.id)}
                      >
                        삭제
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default Memos;
