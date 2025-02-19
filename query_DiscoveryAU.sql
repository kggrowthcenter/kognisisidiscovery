SELECT  
    u.name, 
    u.email, 
    u.created_at AS 'created_at',
    'Discovery' AS platform,  -- Menambahkan kolom platform dengan nilai 'Discovery'
    CASE 
        WHEN ubr.created_at IS NOT NULL THEN 'Active'  -- Jika terdapat Test Date maka status Active
        ELSE 'Passive'  -- Jika tidak ada Test Date maka status Passive
    END AS learner_status
FROM user_results ur
JOIN users u ON 
    ur.user_id = u.id
LEFT JOIN user_bundle_result_user_result ubrur ON 
    ur.id = ubrur.user_result_id
LEFT JOIN user_bundle_results ubr ON 
    ubrur.user_bundle_result_id = ubr.id
ORDER BY u.name ASC, u.created_at DESC;
