
#ifndef BOOST_MPL_SET_AUX_EMPTY_IMPL_HPP_INCLUDED
#define BOOST_MPL_SET_AUX_EMPTY_IMPL_HPP_INCLUDED

// Copyright Aleksey Gurtovoy 2003-2004
//
// Distributed under the Boost Software License, Version 1.0. 
// (See accompanying file LICENSE_1_0.txt or copy at 
// http://www.boost.org/LICENSE_1_0.txt)
//
// See http://www.boost.org/libs/mpl for documentation.

// $Id: empty_impl.hpp 49267 2008-10-11 06:19:02Z agurtovoy $
// $Date: 2008-10-10 23:19:02 -0700 (Fri, 10 Oct 2008) $
// $Revision: 49267 $

#include <boost/mpl/empty_fwd.hpp>
#include <boost/mpl/not.hpp>
#include <boost/mpl/set/aux_/tag.hpp>

namespace boost { namespace mpl {

template<>
struct empty_impl< aux::set_tag >
{
    template< typename Set > struct apply
        : not_< typename Set::size >
    {
    };
};

}}

#endif // BOOST_MPL_SET_AUX_EMPTY_IMPL_HPP_INCLUDED
