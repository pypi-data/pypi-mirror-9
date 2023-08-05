<%!
    import calendar
    import hashlib
%>
% for year, months in blogtree.items():
${year}
${''.join('#' for _ in range(len(str(year))))}

% for month, posts in months.items():
${calendar.month_name[month]}
${''.join('=' for _ in range(len(calendar.month_name[month])))}

% for post in posts:
    - |${post['id']}|_
% endfor

% for post in posts:
.. |${post['id']}| raw:: html

    ${post['docutils']['title'] | n}

.. _${post['id']}: ${post['path']}
% endfor

% endfor

% endfor
