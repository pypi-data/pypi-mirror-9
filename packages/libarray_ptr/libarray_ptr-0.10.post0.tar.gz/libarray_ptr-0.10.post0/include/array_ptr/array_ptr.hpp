/* array_ptr
 *
 * a simple c style array ptr/size wrapper template for c++
 * with stl container functionality
 * and support for std::vector and boost::array
 *
 * Copyright (C) 2011-2013 Stefan Zimmermann <zimmermann.code@gmail.com>
 *
 * array_ptr is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * array_ptr is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with array_ptr.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef __STZ_ARRAY_PTR_HPP
#define __STZ_ARRAY_PTR_HPP

#include <cstdlib>

#include <array>
#include <vector>

#include <boost/array.hpp>
#include <boost/tuple/tuple.hpp>

namespace stz
{
  template<typename T>
  class array_ptr
  {
  private:
    T *values;
    std::size_t _size;

  public:
    typedef T value_type;

    typedef T* iterator;
    typedef const T* const_iterator;

    inline array_ptr(T *values = NULL, std::size_t size = 0) :
      values(values),
      _size(size)
    {}

    inline array_ptr(const array_ptr<T> &values) :
      values(values.values),
      _size(values._size)
    {}

    inline array_ptr(std::vector<T> &values) :
      values(&values[0]),
      _size(values.size())
    {}

    template<std::size_t SIZE>
    inline array_ptr(std::array<T, SIZE> &values) :
      values(values.c_array()),
      _size(SIZE)
    {}

    template<std::size_t SIZE>
    inline array_ptr(boost::array<T, SIZE> &values) :
      values(values.c_array()),
      _size(SIZE)
    {}

    template<typename S>
    inline array_ptr(const std::pair<T*, S> &values_and_size) :
      values(values_and_size.first), _size(values_and_size.second)
    {}

    template<typename S>
    inline array_ptr(const boost::tuple<T*, S> &values_and_size) :
      values(values_and_size.template get<0>()),
      _size(values_and_size.template get<1>())
    {}

    inline void reset(array_ptr<T> &values)
    {
      *this = values;
    }

    inline void reset(T *values = NULL, std::size_t size = 0)
    {
      this->values = values;
      this->_size = size;
    }

    inline void reset(std::vector<T> &values)
    {
      this->values = &values[0];
      this->_size = values.size();
    }

    template<std::size_t SIZE>
    inline void reset(boost::array<T, SIZE> &values)
    {
      this->values = values.c_array();
      this->_size = SIZE;
    }

    template<typename S>
    inline void reset(const std::pair<T*, S> &values_and_size)
    {
      this->values = values_and_size.first;
      this->_size = values_and_size.second;
    }

    template<typename S>
    inline void reset(const boost::tuple<T*, S> &values_and_size)
    {
      this->values = values_and_size.template get<0>();
      this->_size = values_and_size.template get<1>();
    }

    inline T* get()
    {
      return this->values;
    }

    inline const T* get() const
    {
      return this->values;
    }

    inline operator T*()
    {
      return this->values;
    }

    inline operator const T*() const
    {
      return this->values;
    }

    inline T& operator[](std::size_t index)
    {
      return this->values[index];
    }

    inline const T& operator[](std::size_t index) const
    {
      return this->values[index];
    }

    inline std::size_t size() const
    {
      return this->_size;
    }

    inline iterator begin()
    {
      return iterator(this->values);
    }

    inline iterator end()
    {
      return iterator(this->values + this->_size);
    }

    inline const_iterator begin() const
    {
      return const_iterator(this->values);
    }

    inline const_iterator end() const
    {
      return const_iterator(this->values + this->_size);
    }

    inline const_iterator cbegin() const
    {
      return const_iterator(this->values);
    }

    inline const_iterator cend() const
    {
      return const_iterator(this->values + this->_size);
    }

    template<typename SEP>
    inline std::ostream& out(std::ostream &out, const SEP &separator) const
    {
      bool is_first = true;
      for (const T &value : *this)
        (is_first ? (is_first = false, out) : (out << separator)) << value;

      return out;
    }

    inline std::ostream& out(std::ostream &out) const
    {
      return this->out(out, ' ');
    }
  };
}

template<typename T>
inline std::ostream& operator<<
(std::ostream &out, const stz::array_ptr<T> &array)
{
  return array.out(out);
}

#endif
