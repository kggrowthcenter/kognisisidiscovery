SELECT  
    u.name, 
    u.email, 
    '000000' AS nik,  -- Menambahkan kolom 'nik' dengan nilai tetap '000000'
    CASE 
        WHEN ubr.bundle_id = 1 THEN 'GI'
        WHEN ubr.bundle_id = 2 THEN 'LEAN'
        WHEN ubr.bundle_id = 3 THEN 'ELITE'
        WHEN ubr.bundle_id = 4 THEN 'Genuine'
        WHEN ubr.bundle_id = 5 THEN 'Astaka'
    END AS title,  -- Mengubah nama 'bundle_name' menjadi 'title'
    ubr.created_at AS last_updated,  -- Memilih 'created_at' sebagai 'last_updated'
    1200 AS duration,  -- Menambahkan kolom tetap 'duration' dengan nilai '1200'
    'Assessment' AS type,  -- Menambahkan kolom tetap 'type' dengan nilai 'Assessment'
    'Discovery' AS platform,  -- Menambahkan kolom tetap 'platform' dengan nilai 'Discovery'
    i.name AS institution,  -- Menambahkan kolom 'Institution'
    c.id AS 'Customer ID',  -- Menambahkan kolom 'customer_id'
    c.last_education AS last_education,  -- Menambahkan kolom 'Last Education'
    c.date_of_birth AS date_of_birth,
    c.company AS company, -- Menambahkan kolom 'Company'
    c.company AS Company, -- Menambahkan kolom 'Company'
    c.gender AS gender, -- Menambahkan kolom 'Gender'
    p.name AS Province,  -- Menambahkan kolom 'Province'
    t.name AS 'Test Name',  -- Menambahkan kolom 'Test Name'
    ur.test_result_attribute->>'$[0].name' AS typology,  -- Menambahkan kolom 'typology' dari atribut 'test_result_attribute'
    LEFT(ur.total_score, 2) AS total_score,  -- Mengambil dua angka pertama dari 'total_score'
    ubr.result_name AS final_result  -- Menambahkan kolom 'final_result' tanpa koma di akhir
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
ORDER BY title ASC, u.name ASC, ubr.created_at DESC, ur.total_score DESC;
