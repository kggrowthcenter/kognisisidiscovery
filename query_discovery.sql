SELECT  
    u.email, 
    u.name, 
    u.phone,
    u.created_at AS 'Register Date',
    ubr.created_at AS 'Test Date',
    CASE 
        WHEN ubr.bundle_id = 1 THEN 'GI'
        WHEN ubr.bundle_id = 2 THEN 'LEAN'
        WHEN ubr.bundle_id = 3 THEN 'ELITE'
        WHEN ubr.bundle_id = 4 THEN 'Genuine'
        WHEN ubr.bundle_id = 5 THEN 'Astaka'
    END AS bundle_name,
    t.name AS 'Test Name',
    ur.test_result_attribute->>'$[0].name' AS typology,
    ur.total_score,
    ubr.result_name AS final_result,
    p.name AS 'Province',           
    i.name AS 'Institution',        
    c.last_education AS 'Last Education',
    c.id AS 'Customer ID'  -- Customer ID added
FROM user_results ur
LEFT JOIN tests t ON
    ur.test_id = t.id
JOIN users u ON 
    ur.user_id = u.id
JOIN user_bundle_result_user_result ubrur ON 
    ur.id = ubrur.user_result_id
JOIN user_bundle_results ubr ON 
    ubrur.user_bundle_result_id = ubr.id
LEFT JOIN customers c ON
    u.id = c.user_id
LEFT JOIN provinces p ON
    c.province_id = p.id
LEFT JOIN institutions i ON
    c.institution_id = i.id
ORDER BY bundle_name ASC, u.name ASC, ubr.created_at DESC, ur.total_score DESC;