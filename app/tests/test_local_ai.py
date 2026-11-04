import io
import json
import pytest
from app import Career, db
from services import ai

@pytest.mark.parametrize('url', [
    'https://example.test', 'http://example.test:11434',
    'http://127.0.0.1.evil.test', 'http://127.0.0.1@evil.test',
    'http://user:password@127.0.0.1:11434', 'http://127.0.0.1:11434/api',
    'http://127.0.0.1:11434?proxy=external', 'http://127.0.0.1:invalid',
])
def test_model_requests_reject_external_or_ambiguous_hosts(monkeypatch, url):
    monkeypatch.setenv('OLLAMA_MODEL', 'fixture-model')
    monkeypatch.setenv('OLLAMA_URL', url)
    assert not ai.configured()
    with pytest.raises(ai.AIUnavailable):
        ai.local_url()

def test_native_local_chat_and_stream_transport(monkeypatch):
    monkeypatch.setattr(ai, 'GENERATION_LOCKED', False)
    monkeypatch.setenv('OLLAMA_MODEL', 'fixture-model')
    monkeypatch.setenv('OLLAMA_URL', 'http://localhost:11434')
    seen=[]
    class LocalTransport:
        def open(self, request, timeout):
            seen.append(request)
            body=json.loads(request.data)
            assert request.full_url == 'http://127.0.0.1:11434/api/chat'
            assert not request.has_header('Authorization')
            assert body['model'] == 'fixture-model'
            if body['stream']:
                return io.BytesIO(b'{"message":{"content":"One "},"done":false}\n{"message":{"content":"answer"},"done":true}\n')
            return io.BytesIO(b'{"message":{"content":"Local answer"},"done":true}')
    handlers=[]
    def opener(*items):
        handlers.extend(items)
        return LocalTransport()
    monkeypatch.setattr(ai, 'build_opener', opener)
    assert ai.complete('System', 'Question') == 'Local answer'
    assert ''.join(ai.stream([{'role':'user','content':'Question'}])) == 'One answer'
    assert len(seen) == 2
    assert any(isinstance(h,ai.ProxyHandler) and h.proxies == {} for h in handlers)
    assert any(isinstance(h,ai.NoRedirects) for h in handlers)
    assert ai.NoRedirects().redirect_request(None,None,302,'',{},'https://example.test') is None

def test_native_stream_requires_completion_marker(monkeypatch):
    monkeypatch.setattr(ai, 'GENERATION_LOCKED', False)
    monkeypatch.setattr(ai, '_request', lambda *args: io.BytesIO(b'{"message":{"content":"partial"},"done":false}\n'))
    with pytest.raises(ai.AIUnavailable, match='interrupted'):
        list(ai.stream([]))

def test_local_cloud_models_are_rejected(monkeypatch):
    monkeypatch.setenv('OLLAMA_MODEL', 'example:cloud')
    assert not ai.configured()
    with pytest.raises(ai.AIUnavailable):
        ai.model()

def test_offline_index_and_matching_ignore_old_provider_vectors(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Local matching must not perform network requests')
    monkeypatch.setattr(ai, 'build_opener', forbidden)
    entries=Career.query.all()
    for entry in entries:
        entry.embedding=[100,1]
        entry.embedding_model='obsolete-provider'
    before,_=ai.rank('Python SQL software', entries)
    assert ai.refresh_embeddings(entries)==len(entries)
    db.session.commit()
    assert all(e.embedding_model=='local-term-frequency-v1' for e in entries)
    after,_=ai.rank('Python SQL software', entries)
    assert [(s,c.id) for s,c in before] == [(s,c.id) for s,c in after]
    entries[0].description += ' New editorial detail.'
    assert ai.rank('Python SQL software', entries)[0]
