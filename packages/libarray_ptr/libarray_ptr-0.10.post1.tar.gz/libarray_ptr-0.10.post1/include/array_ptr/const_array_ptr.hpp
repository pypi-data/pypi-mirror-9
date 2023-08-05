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

#ifndef __STZ_CONST_ARRAY_PTR_HPP
#define __STZ_CONST_ARRAY_PTR_HPP

#include "array_ptr.hpp"

namespace stz
{
  template<typename T>
  class const_array_ptr : public array_ptr<const T>
  {
  public:
    inline const_array_ptr(const T *values = NULL, std::size_t size = 0) :
      array_ptr<const T>(values, size)
    {}

    inline const_array_ptr(const array_ptr<T> &values) :
      array_ptr<const T>(values.get(), values.size())
    {}

    inline const_array_ptr(const std::vector<T> &values) :
      array_ptr<const T>(&values[0], values.size())
    {}

    template<std::size_t SIZE>
    inline const_array_ptr(const std::array<T, SIZE> &values) :
      array_ptr<const T>(values.data(), SIZE)
    {}

    template<std::size_t SIZE>
    inline const_array_ptr(const boost::array<T, SIZE> &values) :
      array_ptr<const T>(values.data(), SIZE)
    {}

    template<typename S>
    inline const_array_ptr(const std::pair<T*, S> &values_and_size) :
      array_ptr<const T>(values_and_size.first, values_and_size.second)
    {}

    template<typename S>
    inline const_array_ptr(const std::pair<const T*, S> &values_and_size) :
      array_ptr<const T>(values_and_size)
    {}

    template<typename S>
    inline const_array_ptr(const boost::tuple<T*, S> &values_and_size) :
      array_ptr<const T>(values_and_size.template get<0>(),
                         values_and_size.template get<1>())
    {}

    template<typename S>
    inline const_array_ptr
    (const boost::tuple<const T*, S> &values_and_size) :

      array_ptr<const T>(values_and_size)
    {}

    inline void reset(const T *values = NULL, std::size_t size = 0)
    {
      this->array_ptr<const T>::reset(values, size);
    }

    inline void reset(const array_ptr<T> &values)
    {
      this->array_ptr<const T>::reset(values.get(), values.size());
    }

    inline void reset(const std::vector<T> &values)
    {
      this->array_ptr<const T>::reset(&values[0], values.size());
    }

    template<std::size_t SIZE>
    inline void reset(const boost::array<T, SIZE> &values)
    {
      this->array_ptr<const T>::reset(values.data(), SIZE);
    }

    template<typename S>
    inline void reset(const std::pair<T*, S> &values_and_size)
    {
      this->array_ptr<const T>::reset
        (values_and_size.first, values_and_size.second);
    }

    template<typename S>
    inline void reset(const std::pair<const T*, S> &values_and_size)
    {
      this->array_ptr<const T>::reset(values_and_size);
    }

    template<typename S>
    inline void reset(const boost::tuple<T*, S> &values_and_size)
    {
      this->array_ptr<const T>::reset
        (values_and_size.template get<0>(),
         values_and_size.template get<1>());
    }

    template<typename S>
    inline void reset(const boost::tuple<const T*, S> &values_and_size)
    {
      this->array_ptr<const T>::reset(values_and_size);
    }
  };
}

template<typename T>
inline std::ostream&
operator<<(std::ostream &out, const stz::const_array_ptr<T> &array)
{
  return operator<<
    (out, static_cast<const stz::array_ptr<const T>&>(array));
}

#endif
