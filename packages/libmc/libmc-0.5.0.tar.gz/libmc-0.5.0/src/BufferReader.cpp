#include <cassert>
#include <cstring>
#include <stdexcept>
#include <algorithm>

#include "BufferReader.h"
#include "Utility.h"

namespace douban {
namespace mc {
namespace io {

BufferReader::BufferReader()
  :m_capacity(0), m_size(0), m_readLeft(0), m_nextPreferedDataBlockSize(0) {
    m_blockWriteIterator = m_dataBlockList.end();
    m_blockReadCursor.iterator = m_dataBlockList.end();
    m_blockReadCursor.offset = 0;
}


BufferReader::~BufferReader() {
  for (DataBlockListIterator it = m_dataBlockList.begin();
       it != m_dataBlockList.end(); ++it) {
    if (!it->reusable()) {
      log_warn("delete a DataBlock(%p) in use. nBytes: %lu.\n---\n%s\n---\n",
               &*it, it->nBytesRef(), (*it)[0]);
    }
  }
  m_dataBlockList.clear();
  m_capacity = 0;
  m_size = 0;
  m_readLeft = 0;
}


void BufferReader::reset() {

  // assume all datablocks are reusable(ref == 0)
  int i = 0;
  DataBlock* dbPtr = NULL;
  for (DataBlockListIterator it = m_dataBlockList.begin();
       it != m_dataBlockList.end(); ++it, ++i) {
    dbPtr = &*it;
    if (!dbPtr->reusable()) {
      log_warn("A DataBlock(%p) in use is backspace-ed. "
               "This should ONLY be happened on error. "
               "nBytes: %lu:",
               dbPtr, dbPtr->nBytesRef());
      utility::fprintBuffer(stderr, dbPtr->at(0), std::min(dbPtr->nBytesRef(), 128UL));
    }
    dbPtr->reset();
    if (i > 0) {
      m_capacity -= dbPtr->capacity();
    }
  }
  if (i > 1) {
    m_dataBlockList.resize(1);
  }

  m_size = 0;
  m_readLeft = 0;
  m_blockWriteIterator = m_dataBlockList.begin();
  m_blockReadCursor.iterator = m_dataBlockList.begin();
  m_blockReadCursor.offset = 0;
}


void BufferReader::_resetHEAD() {
  for (DataBlockListIterator it = m_dataBlockList.begin();
       it != m_dataBlockList.end(); ++it) {
    it->acquire(it->size() - it->nBytesRef());
  }
  m_blockReadCursor.iterator = m_dataBlockList.begin();
  m_blockReadCursor.offset = 0;
  m_blockReadCursor.offset = 0;
  m_readLeft = m_size;
}


size_t BufferReader::prepareWriteBlock(size_t len) {

  if (m_blockWriteIterator != m_dataBlockList.end() &&
      m_blockWriteIterator->getWriteLeft() == 0) {
    ++m_blockWriteIterator;
  }

  assert(m_blockWriteIterator == m_dataBlockList.end() ||
         m_blockWriteIterator->getWriteLeft() > 0);

  DataBlock *dbPtr = NULL;

  if (m_blockWriteIterator == m_dataBlockList.end()) {
    // create new block
    size_t preferedSize = std::max(len, DataBlock::minCapacity());
    m_dataBlockList.push_back(DataBlock());
    dbPtr = &m_dataBlockList.back();
    dbPtr->init(preferedSize);
    m_capacity += dbPtr->capacity();

    assert(dbPtr->size() == 0);
    assert(dbPtr->getWriteLeft() == dbPtr->capacity());

    m_blockWriteIterator = --m_dataBlockList.end();
  } else {
    dbPtr = &*m_blockWriteIterator;
  }

  // init read cursor when the first data block is created
  if (m_readLeft == 0) {
    m_blockReadCursor.iterator = m_blockWriteIterator;
    m_blockReadCursor.offset = dbPtr->size();
  }

  return std::min(len, dbPtr->getWriteLeft());
}


char* BufferReader::getWritePtr() {
  if (m_blockWriteIterator != m_dataBlockList.end()) {
    return m_blockWriteIterator->getWritePtr();
  }
  return NULL;
}


void BufferReader::commitWrite(size_t len) {
  assert(m_blockWriteIterator->size() + len <= m_blockWriteIterator->capacity());
  m_blockWriteIterator->push(len);
  if (m_blockWriteIterator->size() + len == m_blockWriteIterator->capacity()) {
    ++m_blockWriteIterator;
  }
  m_size += len;
  m_readLeft += len;
}


void BufferReader::write(char* ptr, size_t len, bool copying) {
  // TODO copying = false, and take over ptr
  size_t n_copied = 0;
  while (len > 0) {
    size_t n_available = this->prepareWriteBlock(len);
    std::memcpy(this->getWritePtr(), ptr + n_copied, n_available);
    this->commitWrite(n_available);

    len -= n_available;
    n_copied += n_available;
  }
}


size_t BufferReader::capacity() {
  return m_capacity;
}

size_t BufferReader::size() {
  return m_size;
}

size_t BufferReader::nDataBlock() {
  return m_dataBlockList.size();
}

size_t BufferReader::nBytesRef() {
  size_t t = 0;
  for (DataBlockListIterator it = m_dataBlockList.begin();
      it != m_dataBlockList.end(); ++it) {
    t += it->nBytesRef();
  }
  return t;
}


const char BufferReader::peek(err_code_t& err, size_t offset) const {
  err = OK_ERR;
  if (offset >= m_readLeft) {
    err = INCOMPLETE_BUFFER_ERR;
    return '\0';
  }
  DataCursor cur = m_blockReadCursor;

  while (offset > 0) {
    if (offset < cur.iterator->size() - cur.offset) {
      cur.offset += offset;
      offset = 0;
    } else {
      if (cur.iterator != m_blockWriteIterator) {
        offset -= (cur.iterator->size() - cur.offset);
        ++cur.iterator;
        cur.offset = 0;
      } else {
        err = INCOMPLETE_BUFFER_ERR;
        return '\0';
      }
    }
  }

  return charAtCursor(cur);
}


size_t BufferReader::readUntil(err_code_t& err, char value, TokenData& tokenData) {
  assert(tokenData.size() == 0);
  err = OK_ERR;
  DataCursor endCur = m_blockReadCursor;
  DataBlock * dbPtr = NULL;
  size_t nSize = 0;
  while (endCur.iterator != m_dataBlockList.end()) {
    dbPtr = &*endCur.iterator;
    size_t pos = dbPtr->find(value, endCur.offset);
    if (pos != dbPtr->size()) {
      endCur.offset = pos;
      break;
    }
    ++endCur.iterator;
    endCur.offset = 0;
  }

  if (endCur.iterator == m_dataBlockList.end()) {
    err = INCOMPLETE_BUFFER_ERR;
    return 0;
  }

  while (m_blockReadCursor != endCur) {
    dbPtr = &*m_blockReadCursor.iterator;

    DataBlockSlice dbs;
    dbs.iterator = m_blockReadCursor.iterator;
    dbs.offset =  m_blockReadCursor.offset;
    if (m_blockReadCursor.iterator == endCur.iterator) {
      dbs.size = endCur.offset - m_blockReadCursor.offset;
      m_blockReadCursor.offset = endCur.offset;
    } else {
      dbs.size = dbPtr->size() - m_blockReadCursor.offset;
      ++m_blockReadCursor.iterator;
      m_blockReadCursor.offset = 0;
    }

    if (dbs.size > 0) {
      m_readLeft -= dbs.size;
      nSize += dbs.size;
      tokenData.push_back(dbs);
    }
  }
  return nSize;
}


size_t BufferReader::skipUntil(err_code_t& err, char value) {
  err = OK_ERR;
  DataCursor endCur = m_blockReadCursor;
  DataBlock * dbPtr = NULL;
  size_t nSize = 0;
  while (endCur.iterator != m_dataBlockList.end()) {
    dbPtr = &*endCur.iterator;
    size_t pos = dbPtr->find(value, endCur.offset);
    if (pos != dbPtr->size()) {
      endCur.offset = pos;
      break;
    }
    ++endCur.iterator;
    endCur.offset = 0;
  }

  if (endCur.iterator == m_dataBlockList.end()) {
    err = INCOMPLETE_BUFFER_ERR;
    return 0;
  }

  while (m_blockReadCursor != endCur) {
    dbPtr = &*m_blockReadCursor.iterator;
    size_t len = 0;
    if (m_blockReadCursor.iterator == endCur.iterator) {
      len = endCur.offset - m_blockReadCursor.offset;
      m_blockReadCursor.offset = endCur.offset;
    } else {
      len = dbPtr->size() - m_blockReadCursor.offset;
      ++m_blockReadCursor.iterator;
      m_blockReadCursor.offset = 0;
    }

    if (len > 0) {
      dbPtr->release(len);
      m_readLeft -= len;
      nSize += len;
    }
  }
  return nSize;
}


void BufferReader::readUnsigned(err_code_t& err, uint64_t& value) {
  err = OK_ERR;
  value = 0ULL;
  if (m_readLeft < 2) {
    err = INCOMPLETE_BUFFER_ERR;
    return;
  }

  DataCursor endCur = m_blockReadCursor;
  DataBlock* dbPtr = NULL;
  while (endCur.iterator != m_dataBlockList.end()) {
    dbPtr = &*endCur.iterator;
    size_t pos = dbPtr->findNotNumeric(endCur.offset);
    if (pos != dbPtr->size()) {
      endCur.offset = pos;
      break;
    }
    ++endCur.iterator;
    endCur.offset = 0;
  }

  if (m_blockReadCursor == endCur) {
    err = PROGRAMMING_ERR;
    return;
  }

  if (endCur.iterator == m_dataBlockList.end()) {
    err = INCOMPLETE_BUFFER_ERR;
    return;
  }

  size_t offset = 0;
  while (m_blockReadCursor != endCur) {
    dbPtr = &*m_blockReadCursor.iterator;
    offset = m_blockReadCursor.offset;

    size_t len = 0, j = 0;

    if (m_blockReadCursor.iterator == endCur.iterator) {
      len = endCur.offset - m_blockReadCursor.offset;
      m_blockReadCursor.offset = endCur.offset;
    } else {
      len = dbPtr->size() - m_blockReadCursor.offset;
      ++m_blockReadCursor.iterator;
      m_blockReadCursor.offset = 0;
    }
    for (j = 0; j < len; j++) {
      value = value * 10ULL + (*((*dbPtr)[offset + j]) - '0');
    }

    m_readLeft -= len;
    dbPtr->release(len);
  }
}


void BufferReader::readBytes(err_code_t& err, size_t len, TokenData& tokenData) {
  assert(len >= 0);
  assert(tokenData.size() == 0);
  err = OK_ERR;
  if (len == 0) {
    return;
  }
  if (len > m_readLeft) {
    err = INCOMPLETE_BUFFER_ERR;
    return;
  }
  m_readLeft -= len;

  while (len > 0) {
    DataBlockSlice dbs;
    dbs.iterator = m_blockReadCursor.iterator;
    dbs.offset = m_blockReadCursor.offset;

    size_t maxToRead = m_blockReadCursor.iterator->size() - m_blockReadCursor.offset;

    if (len < maxToRead) {
      dbs.size = len;
      m_blockReadCursor.offset += len;
      len = 0;
    } else { // len == maxToRead
      dbs.size = maxToRead;
      len -= maxToRead;
      ++m_blockReadCursor.iterator;
      m_blockReadCursor.offset = 0;
    }
    tokenData.push_back(dbs);
  }
}


void BufferReader::expectBytes(err_code_t& err, const char* str, size_t len) {
  assert(len > 0);
  err = OK_ERR;
  if (len > m_readLeft) {
    err = INCOMPLETE_BUFFER_ERR;
    return;
  }
  m_readLeft -= len;
  int pos = 0;

  DataBlock* dbPtr = NULL;
  while (len > 0) {
    dbPtr = &*(m_blockReadCursor.iterator);
    size_t maxToRead = dbPtr->size() - m_blockReadCursor.offset;

    if (len < maxToRead) {
      if (strncmp(dbPtr->at(m_blockReadCursor.offset), str + pos, len) != 0) {
        err = PROGRAMMING_ERR;
        return;
      }
      pos += len;
      dbPtr->release(len);
      m_blockReadCursor.offset += len;
      len = 0;
    } else { // len == maxToRead
      if (strncmp(dbPtr->at(m_blockReadCursor.offset), str + pos, maxToRead) != 0) {
        err = PROGRAMMING_ERR;
        return;
      }
      pos += maxToRead;
      dbPtr->release(maxToRead);
      len -= maxToRead;
      ++m_blockReadCursor.iterator;
      m_blockReadCursor.offset = 0;
    }
  }
}


void BufferReader::skipBytes(err_code_t& err, size_t len) {
  assert(len > 0);
  err = OK_ERR;
  if (len > m_readLeft) {
    err = INCOMPLETE_BUFFER_ERR;
    return;
  }
  m_readLeft -= len;
  DataBlock* dbPtr = NULL;
  while (len > 0) {
    dbPtr = &*m_blockReadCursor.iterator;
    size_t maxToRead = dbPtr->size() - m_blockReadCursor.offset;

    if (len < maxToRead) {
      dbPtr->release(len);
      m_blockReadCursor.offset += len;
      len = 0;
    } else { // len == maxToRead
      dbPtr->release(maxToRead);
      len -= maxToRead;
      ++m_blockReadCursor.iterator;
      m_blockReadCursor.offset = 0;
    }
  }
}


void BufferReader::print() {
  fprintf(stderr, "BufferReader(addr: %p, nDataBlock: %lu, nSize: %lu)\n---\n",
          this, this->nDataBlock(), this->m_size);
  for (DataBlockListIterator it = m_dataBlockList.begin();
      it != m_dataBlockList.end(); ++it) {
    fprintf(stderr, "%.*s", static_cast<int>(it->size()), it->at(0));
  }
  fprintf(stderr, "\n---\n");
}


size_t BufferReader::getNextPreferedDataBlockSize() {
  size_t tmp = m_nextPreferedDataBlockSize == 0 ?
      DataBlock::minCapacity() :
      m_nextPreferedDataBlockSize;
  m_nextPreferedDataBlockSize = DataBlock::minCapacity();
  return tmp;
}


void BufferReader::setNextPreferedDataBlockSize(size_t n) {
  m_nextPreferedDataBlockSize = n;
}

void freeTokenData(TokenData& td) {
  for (TokenData::const_iterator it = td.begin(); it != td.end(); ++it) {
    it->iterator->release(it->size);
  }
}

void printTokenData(TokenData& td) {
  fprintf(stderr, "[");
  for (TokenData::const_iterator i = td.begin(); i != td.end(); ++i) {
    fprintf(stderr, "%.*s", static_cast<int>(i->size), i->iterator->at(i->offset));
  }
  fprintf(stderr, "]\r\n");
}

char* parseTokenData(TokenData& td, size_t reserved) {
  if (reserved == 0) {
    return NULL;
  }
  if (td.size() == 1) {
    TokenData::const_iterator it = td.begin();
    assert(it->size == reserved);
    return it->iterator->at(it->offset);
  }

  char* ptr = new char[reserved];
  size_t pos = 0;
  for (TokenData::const_iterator it = td.begin(); it != td.end(); ++it) {
    if (pos + it->size > reserved) {
      log_err("programmer error: overflow in parseTokenData(%p), reserved: %lu",
              &td, reserved);
      return NULL;
    }

    memcpy(ptr + pos, it->iterator->at(it->offset), it->size);
    pos += (it->size);
  }
  assert(reserved == pos);
  return ptr;
}


void copyTokenData(const TokenData& src, TokenData& dst) {
  if (src.size() == 0) {
    return;
  }
  assert(dst.size() == 0);
  dst = src;
  assert(dst.size() == src.size());
  assert(src.size() == 0 || (dst.begin() != src.begin()));
  for (TokenData::const_iterator it = dst.begin(); it != dst.end(); ++it) {
    it->iterator->acquire(it->size);
  }
}



} // namespace io
} // namespace mc
} // namespace douban
