//
// steady_timer.hpp
// ~~~~~~~~~~~~~~~~
//
// Copyright (c) 2003-2012 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#ifndef BOOST_ASIO_STEADY_TIMER_HPP
#define BOOST_ASIO_STEADY_TIMER_HPP

#if defined(_MSC_VER) && (_MSC_VER >= 1200)
# pragma once
#endif // defined(_MSC_VER) && (_MSC_VER >= 1200)

#include <boost/asio/detail/config.hpp>

#if defined(BOOST_ASIO_HAS_STD_CHRONO) \
  || defined(BOOST_ASIO_HAS_BOOST_CHRONO) \
  || defined(GENERATING_DOCUMENTATION)

#if defined(BOOST_ASIO_HAS_STD_CHRONO)
# include <chrono>
#elif defined(BOOST_ASIO_HAS_BOOST_CHRONO)
# include <boost/chrono/system_clocks.hpp>
#endif

#include <boost/asio/basic_waitable_timer.hpp>

namespace boost {
namespace asio {

#if defined(GENERATING_DOCUMENTATION)
/// Typedef for a timer based on the steady clock.
/**
 * This typedef uses the C++11 @c &lt;chrono&gt; standard library facility, if
 * available. Otherwise, it may use the Boost.Chrono library. To explicitly
 * utilise Boost.Chrono, use the basic_waitable_timer template directly:
 * @code
 * typedef basic_waitable_timer<boost::chrono::steady_clock> timer;
 * @endcode
 */
typedef basic_waitable_timer<chrono::steady_clock> steady_timer;
#elif defined(BOOST_ASIO_HAS_STD_CHRONO)
# if defined(BOOST_ASIO_HAS_STD_CHRONO_MONOTONIC_CLOCK)
typedef basic_waitable_timer<std::chrono::monotonic_clock> steady_timer;
# else // defined(BOOST_ASIO_HAS_STD_CHRONO_MONOTONIC_CLOCK)
typedef basic_waitable_timer<std::chrono::steady_clock> steady_timer;
# endif // defined(BOOST_ASIO_HAS_STD_CHRONO_MONOTONIC_CLOCK)
#elif defined(BOOST_ASIO_HAS_BOOST_CHRONO)
typedef basic_waitable_timer<boost::chrono::steady_clock> steady_timer;
#endif

} // namespace asio
} // namespace boost

#endif // defined(BOOST_ASIO_HAS_STD_CHRONO) 
       //   || defined(BOOST_ASIO_HAS_BOOST_CHRONO)
       //   || defined(GENERATING_DOCUMENTATION)

#endif // BOOST_ASIO_STEADY_TIMER_HPP
