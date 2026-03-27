exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const data = JSON.parse(event.body);

    // Honeypot spam check
    if (data.honeypot && data.honeypot.trim() !== '') {
      return { statusCode: 200, body: JSON.stringify({ success: true }) };
    }

    // Validate at least one question is present
    const hasQuestion = [
      data.q_sheriff, data.q_council_pres, data.q_county_exec,
      data.q_council_a, data.q_council_b, data.q_state_senate_34
    ].some(q => q && q.trim().length > 0);

    if (!hasQuestion) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Please fill in at least one question before submitting.' })
      };
    }

    const AIRTABLE_API_KEY = process.env.AIRTABLE_API_KEY;
    const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID;
    const QUESTIONS_TABLE  = 'tblrpuMZRjOEfqHkY';
    const PRIORITIES_TABLE = 'tblUjlOKjxPdPwQYS';

    if (!AIRTABLE_API_KEY || !AIRTABLE_BASE_ID) {
      console.error('Missing environment variables');
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Server configuration error' })
      };
    }

    const submitted = new Date().toISOString();

    const officeMap = {
      q_sheriff:        'Sheriff',
      q_council_pres:   'President of the County Council',
      q_county_exec:    'County Executive',
      q_council_a:      'County Council District A',
      q_council_b:      'County Council District B',
      q_state_senate_34:'State Senate District 34',
    };

    // ---- STEP 1: Send one row per question to Questions table ----
    const questionResults = [];

    for (const [key, office] of Object.entries(officeMap)) {
      const question = data[key] && data[key].trim();
      if (!question) continue;

      const fields = {
        'Name':      data.name || 'Anonymous',
        'Party':     data.party || 'Not specified',
        'Office':    office,
        'Question':  question,
        'Status':    'New',
        'Submitted': submitted,
      };

      const res = await fetch(
        `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${QUESTIONS_TABLE}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${AIRTABLE_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ fields }),
        }
      );

      if (!res.ok) {
        const err = await res.text();
        console.error('Questions table error:', res.status, err);
        throw new Error(`Questions submission failed: ${res.status}`);
      }

      questionResults.push(office);
    }

    // ---- STEP 2: Send ONE priorities row to Community Priorities table ----
    const priorityFields = {
      'Submitted At':   submitted,
      'Development':    parseInt(data.p_development) || 5,
      'Roads':          parseInt(data.p_roads) || 5,
      'Schools':        parseInt(data.p_schools) || 5,
      'Public Safety':  parseInt(data.p_safety) || 5,
      'Taxes':          parseInt(data.p_taxes) || 5,
      'Housing':        parseInt(data.p_housing) || 5,
      'Environment':    parseInt(data.p_environment) || 5,
      'Parks':          parseInt(data.p_parks) || 5,
      'Services':       parseInt(data.p_services) || 5,
      'Other Issues':   data.other_issue || '',
    };

    const priorityRes = await fetch(
      `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${PRIORITIES_TABLE}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${AIRTABLE_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fields: priorityFields }),
      }
    );

    if (!priorityRes.ok) {
      const err = await priorityRes.text();
      console.error('Priorities table error:', priorityRes.status, err);
      // Don't throw here - questions already saved, just log the priority failure
      console.error('Priority submission failed but questions were saved successfully');
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ success: true, submitted: questionResults }),
    };

  } catch (err) {
    console.error('Function error:', err.message);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Something went wrong. Please try again.' }),
    };
  }
};
